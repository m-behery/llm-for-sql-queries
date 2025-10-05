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
    """
    A chatbot interface for OpenAI API that can execute SQL queries and provide natural language responses.
    
    This class handles conversation with OpenAI's chat models, manages session logging,
    executes SQL queries on databases, and translates results between SQL and natural language.
    
    Attributes:
        PROVIDER (str): The AI provider name (e.g., 'openai')
        CHAT_ENDPOINT (str): The OpenAI API endpoint for chat completions
        MESSAGE_LOGS_DB (str): Path to the SQLite database for storing conversation logs
    """
    PROVIDER = ENVIRONMENT.PROVIDER
    CHAT_ENDPOINT = ENVIRONMENT.OPENAI_CHAT_ENDPOINT
    MESSAGE_LOGS_DB = FILEPATHS.MESSAGE_LOGS_DB
    
    def __init__(self, api_key, model, task_template_filepath, db_filepath):
        """
        Initialize the OpenAI chatbot with database and template configuration.
        
        Args:
            api_key (str): OpenAI API key for authentication
            model (str): Name of the OpenAI model to use (e.g., 'gpt-4o-mini')
            task_template_filepath (str): Path to the task template file with system instructions
            db_filepath (str): Path to the SQLite database file for query execution
            
        Note:
            Automatically generates a unique session ID and extracts database schema on initialization.
        """
        self._session_id    = f'session_{secrets.token_urlsafe(32)}'
        self._api_key       = api_key
        self._model         = model
        self._task_template = read_template(task_template_filepath)
        self.db_filepath     = db_filepath
    
    @property
    def session_id(self):
        return self._session_id
    
    @property
    def task_template(self):
        """Get the task template content with system instructions."""
        return self._task_template
    
    @property
    def model(self):
        """Get the OpenAI model name being used."""
        return self._model
    
    @property
    def db_filepath(self):
        """Get the path to the database file."""
        return self._db_filepath
    
    @db_filepath.setter
    def db_filepath(self, value: str):
        """
        Set the database filepath and automatically extract its schema.
        
        Args:
            value (str): Path to the SQLite database file
            
        Note:
            Setting this property triggers database schema extraction and initializes
            the chat history with the schema embedded in the system prompt.
        """
        self._db_filepath = value
        self.db_schema   = extract_db_schema(value)
    
    @property
    def db_schema(self):
        """Get the extracted database schema as SQL CREATE TABLE statements."""
        return self._db_schema
    
    @db_schema.setter
    def db_schema(self, value: str):
        """
        Set the database schema and initialize chat history with system prompt.
        
        Args:
            value (str): Database schema as SQL CREATE TABLE statements
            
        Note:
            This initializes the chat history with a system message containing
            the task template populated with the actual database schema.
        """
        self._db_schema = value
        self._chat_history = [
            {'role': 'system', 'content': Template(self._task_template).substitute({'db_schema': value}) }
        ]
        self.create_message_logs()
        self._create_session()
        self._update_session()

    @classmethod
    def create_message_logs(cls):
        """
        Create the sessions table if it doesn't exist for storing conversation logs.
        
        Creates a table with columns for session tracking, message logs, and timestamps.
        This is called automatically when a new chatbot instance is initialized.
        """
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
        """
        Create a new session record in the message logs database.
        
        Inserts a new session with the generated session ID into the sessions table.
        Called automatically when the database schema is set.
        """
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
        """
        Update the current session with the latest chat history.
        
        Saves the entire chat history as JSON to the sessions table and updates
        the ended_at timestamp to track session activity.
        """
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
        """Get the complete chat history including system, user, and assistant messages."""
        return self._chat_history
    
    def _flush(self):
        """
        Send the current chat history to the OpenAI API and get a response.
        
        Returns:
            dict or None: The JSON response from OpenAI API, or None if the request fails
            
        Raises:
            requests.exceptions.RequestException: If the HTTP request fails (handled internally)
        """
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
        """
        Send a user query to the chatbot and process the response.
        
        This method handles the complete workflow:
        1. Sends user query to OpenAI
        2. If response contains SQL, executes it on the database
        3. Sends SQL results back to OpenAI for natural language explanation
        4. Returns consolidated response details
        
        Args:
            user_query (str): The user's natural language query
            
        Returns:
            dict: Response details containing:
                - session_id (str): Session ID
                - provider (str): AI provider name
                - status (str): 'ok' or 'error'
                - model (str): Model used for response
                - latency_ms (int): Total response time in milliseconds
                - token_usage (dict): Token counts for prompt, completion, and total
                - SQL (str): Generated SQL query or 'N/A'
                - Answer (str): Natural language answer (if available)
                
        Note:
            If SQL is generated and executed, this method makes two API calls with
            a delay between them to avoid rate limiting.
        """
        self._chat_history.append({'role': 'user', 'content': user_query})
        self._update_session()
        with Timer() as t:
            response_json = self._flush()
        response_details = {
            'session_id': self._session_id,
            'provider': self.PROVIDER,
        }
        if response_json:
            response_message = response_json['choices'][0]['message']['content']
            self._chat_history.append({'role': 'system', 'content': response_message})
            self._update_session()
            response_details.update(
                self._extract_response_details(response_json)
            )
            response_details.update({
                'latency_ms': t.elapsed,
                'status': 'ok',
            })
            if 'SQL' in response_details:
                sleep(ENVIRONMENT.DELAY_MS * 1e-3)
                db_query = response_details['SQL']
                rows     = query_db(self._db_filepath, db_query)
                rows_str = '\n'.join(map(str, rows)) if rows is not None else ''
                message = f'SQL:\n{db_query}\n\nOutput:\n{rows_str}'
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
        """
        Extract and parse response details from OpenAI API response.
        
        Args:
            response_json (dict): The JSON response from OpenAI API
            
        Returns:
            dict: Parsed response details including:
                - Original response fields (SQL, Answer, etc.)
                - token_usage: Token counts from the API
                - model: Model name from the API response
                
        Note:
            Expects the response message content to be in JSON format, optionally
            wrapped in markdown code blocks (```json ... ```).
        """
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