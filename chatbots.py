from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import keyring
from string import Template
import os
import logging
import re
import json
import requests
from time import sleep
import secrets
from datetime import datetime

from utils import Timer, read_template, extract_db_schema, query_db
from constants import ENVIRONMENT, FILEPATHS

class OpenAIChatBot:
    
    PROVIDER = ENVIRONMENT.PROVIDER
    CHAT_ENDPOINT = ENVIRONMENT.OPENAI_CHAT_ENDPOINT
    MESSAGE_LOGS_DB = FILEPATHS.MESSAGE_LOGS_DB
    
    def __init__(self, api_key, model, task_template_filepath, db_filepath):
        self._session_id    = f'session_{secrets.token_urlsafe(32)}'
        self._api_key       = api_key
        self._model         = model
        self._task_template = read_template(task_template_filepath)
        self.db_filepath     = db_filepath
    
    @property
    def task_template(self):
        return self._task_template
    
    @property
    def client(self):
        return self._client
    
    @property
    def model(self):
        return self._model
    
    @property
    def db_filepath(self):
        return self._db_filepath
    
    @db_filepath.setter
    def db_filepath(self, value: str):
        self._db_filepath = value
        self.db_schema   = extract_db_schema(value)
    
    @property
    def db_schema(self):
        return self._db_schema
    
    @db_schema.setter
    def db_schema(self, value: str):
        self._db_schema = value
        self._chat_history = [
            {'role': 'system', 'content': Template(self._task_template).substitute({'db_schema': value}) }
        ]
        self.create_message_logs()
        self._create_session()
        self._update_session()

    @classmethod
    def create_message_logs(cls):
        query_db(
            cls.MESSAGE_LOGS_DB,
            '''
            CREATE TABLE IF NOT EXISTS sessions(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                message_log TEXT,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME
            );
            '''
        )

    def _create_session(self):
        query_db(
            self.MESSAGE_LOGS_DB,
            '''
            INSERT INTO sessions
                (session_id) 
            VALUES
                (?);
            ''',
            (
                self._session_id,
            )
        )

    def _update_session(self):
        query_db(
            self.MESSAGE_LOGS_DB,
            '''
            UPDATE sessions 
            SET
                message_log = ?,
                ended_at = CURRENT_TIMESTAMP
            WHERE
                session_id = ?;
            ''',
            (
                json.dumps(self._chat_history, indent=4),
                self._session_id
            )
        )
    
    @property
    def chat_history(self):
        return self._chat_history
    
    def _flush(self):
        try:
            response = requests.post(
                self.CHAT_ENDPOINT,
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self._api_key}',
                },
                json = {
                    'model': self._model,
                    'messages': self._chat_history,
                    'temperature': 1.0,
                },
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            logging.exception('Fatal Error.\nKindly check the error logs for traceback details.')
            return None
    
    def send(self, user_query):
        self._chat_history.append({'role': 'user', 'content': user_query})
        self._update_session()
        with Timer() as t:
            response_json = self._flush()
        response_details = {'provider': self.PROVIDER}
        if response_json:
            response_message = response_json['choices'][0]['message']['content']
            self._chat_history.append({'role': 'system', 'content': response_message})
            self._update_session()
            response_details = self._extract_response_details(response_json)
            response_details.update({
                'latency_ms': t.elapsed,
                'status': 'ok',
            })
            if 'SQL' in response_details:
                sleep(ENVIRONMENT.DELAY_MS * 1e-3)
                db_query = response_details['SQL']
                rows     = query_db(self._db_filepath, db_query)
                rows_str = '\n'.join(map(str, rows))
                message = f'SQL Query:\n{db_query}\n\nOutput:\n{rows_str}'
                self._chat_history.append({'role': 'user', 'content': message})
                self._update_session()
                with Timer() as t:
                    response_json = self._flush()
                if response_json:
                    response_message = response_json['choices'][0]['message']['content']
                    self._chat_history.append({'role': 'system', 'content': response_message})
                    self._update_session()
                    response_b_details = self._extract_response_details(response_json)
                    if 'Answer' in response_b_details:
                        response_details['Answer'] = response_b_details['Answer']
                    response_details.update({
                        'token_usage': {
                            'prompt_tokens'     : response_details['token_usage']['prompt_tokens'] + response_b_details['token_usage']['prompt_tokens'],
                            'completion_tokens' : response_details['token_usage']['completion_tokens'] + response_b_details['token_usage']['completion_tokens'],
                            'total_tokens'      : response_details['token_usage']['total_tokens'] + response_b_details['token_usage']['total_tokens'],
                        },
                        'latency_ms': response_details['latency_ms'] + ENVIRONMENT.DELAY_MS + t.elapsed,
                        'status': 'ok',
                    })
                else:
                    response_details['status'] = 'error'
            else:
                response_details['SQL'] = 'N/A'
        else:
            response_details.update({
                'model': self._model,
                'status': 'error',
            })
        return response_details
    
    @staticmethod
    def _extract_response_details(response_json):
        response_message = response_json['choices'][0]['message']['content']
        details = json.loads(re.sub(r'```(json)?', '', response_message))
        details.update({
            'token_usage': {
                'prompt_tokens'     : response_json['usage']['prompt_tokens'],
                'completion_tokens' : response_json['usage']['completion_tokens'],
                'total_tokens'      : response_json['usage']['total_tokens'],
            },
            'model' : response_json['model'],
        })
        return details