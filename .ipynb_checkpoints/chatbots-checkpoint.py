from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import keyring
from string import Template
import os
import logging
import re
import json
import requests
from utils import Timer, read_task_template
from constants import DB_FILEPATH, LLM_TASK_TEMPLATE_FILEPATH, OPENAI_CHAT_ENDPOINT, PROVIDER, MODEL_NAME

class OpenAIChatBot:
    
    TASK_TEMPLATE = read_task_template(LLM_TASK_TEMPLATE_FILEPATH)
    CHAT_ENDPOINT = OPENAI_CHAT_ENDPOINT
    
    def __init__(self, api_key, model, db_filepath):
        self._api_key   = api_key
        self._model     = model
        self.db_filepath = db_filepath
    
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
        self.db_schema   = self._extract_db_schema(value)
    
    @property
    def db_schema(self):
        return self._db_schema
    
    @db_schema.setter
    def db_schema(self, value: str):
        self._db_schema = value
        self._chat_history = [
            {'role': 'system', 'content': Template(self.TASK_TEMPLATE).substitute({'db_schema': value}) }
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
        response_details = {'provider': PROVIDER}
        if response_json:
            message = response_json['choices'][0]['message']['content']
            self._chat_history.append({'role': 'system', 'content': message})
            response_details = self._extract_response_details(response_json)
            response_details.update({
                'latency_ms': t.elapsed,
                'status': 'ok',
            })
        else:
            response_details.update({
                'model': self._model,
                'status': 'error',
            })
        return response_details
    
    @staticmethod
    def _extract_response_details(response_json):
        message = response_json['choices'][0]['message']['content']
        details = json.loads(re.sub(r'```(json)?', '', message))
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
    def _extract_db_schema(db_filepath: str):
        try:
            conn = sqlite3.connect(DB_FILEPATH)
            cursor = conn.cursor()
            cursor.execute('SELECT sql FROM sqlite_master WHERE type="table";')
            rows = cursor.fetchall()
        finally:
            conn.close()
        create_table_cmds = list(zip(*rows))[0]
        db_schema = '\n'.join(create_table_cmds)
        return db_schema