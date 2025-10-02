from http.server import HTTPServer, BaseHTTPRequestHandler
from string import Template
import logging
import json
import requests

class RequestHandler(BaseHTTPRequestHandler):
    
    _chatbot = None
    
    @classmethod
    def set_chatbot(cls, value):
        cls._chatbot = value
    
    def do_GET(self):
        if self.path == '/api':
            self._send(200, {'message': 'Server is running'})
        else:
            self._send(404, {'error': "Endpoint Doesn't exist"})
    
    def do_POST(self):
        if self.path == '/api/chat':
            json_payload = self._receive()
            if json_payload and 'message' in json_payload:
                user_query = json_payload['message']
            else:
                self._send(400, {'error': 'The JSON payload is missing the "message" field'})
            if self._chatbot:
                openai_response_details = self._chatbot.send(user_query)
                self._send(200, openai_response_details)
            else:
                self._send(500, {'error': 'Chatbot not yet set! Set it within an HTTPServer constructor'})
        else:
            self._send(404, {'error': "Endpoint Doesn't exist"})
    
    def _send(self, status_code, json_payload):
        try:
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            payload_bytes = json.dumps(json_payload, indent=4).encode('utf-8')
            self.wfile.write(payload_bytes)
        except:
            logging.exception(f'Error sending response.\nKindly check the error logs for traceback details.')
            self.send_error(500, 'Internal server error')
            
    def _receive(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return None
            payload_bytes = self.rfile.read(content_length)
            json_payload = json.loads(payload_bytes.decode('utf-8'))
            return json_payload
        except json.JSONDecodeError:
            message = 'Invalid JSON payload.'
            logging.exception(f'{message}\nKindly check the error logs for traceback details.')
            self._send(400, {'error': message})
        except:
            message = 'Error processing request.'
            logging.exception(f'{message}\nKindly check the error logs for traceback details.')
            self._send(400, {'error': message})
        return None

class Server(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, chatbot):
        super().__init__(server_address, RequestHandlerClass)
        RequestHandlerClass.set_chatbot(chatbot)