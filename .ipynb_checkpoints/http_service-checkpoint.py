from http.server import HTTPServer, BaseHTTPRequestHandler
from string import Template
import logging
import json
import requests
import socket

from pyngrok import ngrok  # BONUS -- for remote deployment via an HTTP tunnel with a TLS layer

from utils import read_template

class RequestHandler(BaseHTTPRequestHandler):
    
    _chatbot = None
    _html_template = None
    _css_template = None
    _js_template = None
    
    @classmethod
    def set_chatbot(cls, value):
        cls._chatbot = value
    
    @classmethod
    def set_html_template(cls, value):
        cls._html_template = value
    
    @classmethod
    def set_css_template(cls, value):
        cls._css_template = value
    
    @classmethod
    def set_js_template(cls, value):
        cls._js_template = value
    
    def do_GET(self):
        match self.path:
            case '/':
                if self._html_template:
                    self._serve_html(self._html_template)
                else:
                    self._serve_json(500, {'error': 'HTML template not yet set! Set it within an HTTPServer constructor'})
            case '/style.css':
                if self._css_template:
                    self._serve_css(self._css_template)
                else:
                    self._serve_json(500, {'error': 'CSS template not yet set! Set it within an HTTPServer constructor'})
            case '/script.js':
                if self._js_template:
                    self._serve_js(self._js_template)
                else:
                    self._serve_json(500, {'error': 'JS template not yet set! Set it within an HTTPServer constructor'})
            case '/api':
                self._serve_json(200, {'message': 'API Ready'})
            case '/api/chat':
                self._serve_json(200, {'error': 'This endpoint can only be called using a POST request'})
            case _:
                self._serve_json(404, {'error': "Endpoint Doesn't exist"})
    
    def do_POST(self):
        if self.path == '/api/chat':
            json_payload = self._receive_json()
            if json_payload and 'message' in json_payload:
                user_query = json_payload['message']
            else:
                self._serve_json(400, {'error': 'The JSON payload is missing the "message" field'})
                return
            if self._chatbot:
                openai_response_details = self._chatbot.send(user_query)
                self._serve_json(200, openai_response_details)
            else:
                self._serve_json(500, {'error': 'Chatbot not yet set! Set it within an HTTPServer constructor'})
        else:
            self._serve_json(404, {'error': "Endpoint Doesn't exist"})

    def _serve_html(self, html_content):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except:
            message = 'Error serving HTML'
            logging.exception(f'{message}.\nKindly check the error logs for traceback details.')
            self.send_error(500, message)

    def _serve_css(self, css_content):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/css; charset=utf-8')
            self.end_headers()
            self.wfile.write(css_content.encode('utf-8'))
        except:
            message = 'Error serving CSS'
            logging.exception(f'{message}.\nKindly check the error logs for traceback details.')
            self.send_error(500, message)

    def _serve_js(self, js_content):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.end_headers()
            self.wfile.write(js_content.encode('utf-8'))
        except:
            message = 'Error serving JS'
            logging.exception(f'{message}.\nKindly check the error logs for traceback details.')
            self.send_error(500, message)
    
    def _serve_json(self, status_code, json_payload):
        try:
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            payload_bytes = json.dumps(json_payload, indent=4).encode('utf-8')
            self.wfile.write(payload_bytes)
        except:
            message = 'Error serving JSON'
            logging.exception(f'{message}.\nKindly check the error logs for traceback details.')
            self.send_error(500, message)
            
    def _receive_json(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return None
            payload_bytes = self.rfile.read(content_length)
            json_payload = json.loads(payload_bytes.decode('utf-8'))
            return json_payload
        except json.JSONDecodeError:
            message = 'Invalid JSON payload'
            logging.exception(f'{message}.\nKindly check the error logs for traceback details.')
            self._serve_json(400, {'error': message})
        except:
            message = 'Error processing request'
            logging.exception(f'{message}.\nKindly check the error logs for traceback details.')
            self._serve_json(400, {'error': message})
        return None

class Server(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, chatbot,
                 html_template_filepath, css_template_filepath, js_template_filepath):
        
        super().__init__(server_address, RequestHandlerClass)
        RequestHandlerClass.set_chatbot(chatbot)
        RequestHandlerClass.set_html_template(read_template(html_template_filepath))
        RequestHandlerClass.set_css_template(read_template(css_template_filepath))
        RequestHandlerClass.set_js_template(read_template(js_template_filepath))
    
    def serve_forever(self, public=False):
        print(f'Local Address:\t{self.get_local_address()}')
        if public:
            print(f'Public Address:\t{self.get_public_address()}', end='\n\n')
        try:
            with self:
                super().serve_forever()
        except KeyboardInterrupt:
            print('Keyboard interrupt received.\nServer shutdown successfully!')
    
    def get_local_address(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return f'http://{local_ip}:{self.server_address[1]}'
    
    def get_public_address(self):
        https_tunnel = ngrok.connect(self.server_address[1], bind_tls=True)
        return https_tunnel.public_url
