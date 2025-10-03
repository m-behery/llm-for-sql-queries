from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import keyring
from string import Template
import os
import logging
import re
import json
import requests
from utils import Timer, read_template
from constants import ENVIRONMENT
from time import sleep

class OpenAIChatBot:

    PROVIDER = ENVIRONMENT.PROVIDER
    CHAT_ENDPOINT = ENVIRONMENT.OPENAI_CHAT_ENDPOINT
    
    def __init__(self, api_key, model, task_template_filepath, db_filepath):
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
        self.db_schema   = self.extract_db_schema(value)
    
    @property
    def db_schema(self):
        return self._db_schema
    
    @db_schema.setter
    def db_schema(self, value: str):
        self._db_schema = value
        self._chat_history = [
            {'role': 'system', 'content': Template(self._task_template).substitute({'db_schema': value}) }
        ]
    
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
        with Timer() as t:
            response_json = self._flush()
        response_details = {'provider': self.PROVIDER}
        if response_json:
            response_message = response_json['choices'][0]['message']['content']
            self._chat_history.append({'role': 'system', 'content': response_message})
            response_details = self._extract_response_details(response_json)
            response_details.update({
                'latency_ms': t.elapsed,
                'status': 'ok',
            })
            if 'SQL' in response_details:
                sleep(ENVIRONMENT.DELAY_MS * 1e-3)
                db_query = response_details['SQL']
                rows     = self.query_db(self._db_filepath, db_query)
                rows_str = '\n'.join(map(str, rows))
                message = f'SQL Query:\n{db_query}\n\nOutput:\n{rows_str}'
                self._chat_history.append({'role': 'user', 'content': message})
                with Timer() as t:
                    response_json = self._flush()
                if response_json:
                    response_message = response_json['choices'][0]['message']['content']
                    self._chat_history.append({'role': 'system', 'content': response_message})
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
    
    @staticmethod
    def query_db(db_filepath: str, sqlite_query: str):
        try:
            conn = sqlite3.connect(db_filepath)
            cursor = conn.cursor()
            cursor.execute(sqlite_query)
            rows = cursor.fetchall()
        except:
            logging.exception('Database Error.\nKindly check the error logs for traceback details.')
        finally:
            conn.close()
        return rows
    
    @staticmethod
    def extract_db_schema(db_filepath: str):
        rows = __class__.query_db(
            db_filepath,
            'SELECT sql FROM sqlite_master WHERE type="table";'
        )
        create_table_cmds = list(zip(*rows))[0]
        db_schema = '\n'.join(create_table_cmds)
        return db_schema