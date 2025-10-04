from http.server import HTTPServer, BaseHTTPRequestHandler
from string import Template
import logging
import json
import requests
import socket

from utils import read_template

class RequestHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP request handler for serving the chat application.
    
    This class handles all incoming HTTP requests including:
    - Serving HTML, CSS, and JavaScript templates
    - Processing chat API requests
    - Managing chatbot interactions
    
    Class Attributes:
        _chatbot (OpenAIChatBot): The chatbot instance for processing queries
        _html_template (str): HTML template content
        _css_template (str): CSS stylesheet content  
        _js_template (str): JavaScript code content
    """
    _chatbot = None
    _html_template = None
    _css_template = None
    _js_template = None
    
    @classmethod
    def set_chatbot(cls, value):
        """Set the chatbot instance for processing user queries."""
        cls._chatbot = value
    
    @classmethod
    def set_html_template(cls, value):
        """Set the HTML template content for serving the main page."""
        cls._html_template = value
    
    @classmethod
    def set_css_template(cls, value):
        """Set the CSS template content for styling the application."""
        cls._css_template = value
    
    @classmethod
    def set_js_template(cls, value):
        """Set the JavaScript template content for client-side functionality."""
        cls._js_template = value
    
    def do_GET(self):
        """
        Handle HTTP GET requests for various application endpoints.
        
        Supported endpoints:
        - '/': Serve the main HTML page
        - '/style.css': Serve CSS stylesheet
        - '/script.js': Serve JavaScript file
        - '/api': API status check
        - '/api/chat': Error message for GET on POST-only endpoint
        - All others: 404 Not Found
        
        Returns:
            None: Sends HTTP response directly to client
        """
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
        """
        Handle HTTP POST requests for chat functionality.
        
        Supported endpoints:
        - '/api/chat': Process user chat messages through the chatbot
        
        Expected JSON payload for /api/chat:
        {
            "message": "user query text"
        }
        
        Returns:
            None: Sends HTTP response with chatbot results or error message
        """
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
        """
        Serve HTML content with proper HTTP headers.
        
        Args:
            html_content (str): HTML content to send to client
            
        Returns:
            None: Sends HTTP response or error
        """
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
        """
        Serve CSS content with proper HTTP headers.
        
        Args:
            css_content (str): CSS content to send to client
            
        Returns:
            None: Sends HTTP response or error
        """
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
        """
        Serve JavaScript content with proper HTTP headers.
        
        Args:
            js_content (str): JavaScript content to send to client
            
        Returns:
            None: Sends HTTP response or error
        """
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
        """
        Serve JSON response with proper HTTP headers.
        
        Args:
            status_code (int): HTTP status code to send
            json_payload (dict): JSON-serializable data to send
            
        Returns:
            None: Sends HTTP response or error
        """
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
        """
        Receive and parse JSON payload from request body.
        
        Returns:
            dict or None: Parsed JSON data, or None if error occurs
            
        Note:
            Automatically sends error responses if JSON parsing fails
        """
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
    """
    Custom HTTP server for the chat application with template management.
    
    This class extends HTTPServer to provide:
    - Template configuration for HTML, CSS, and JavaScript
    - Chatbot integration
    - Local and public address resolution
    - ngrok tunnel support for public access
    
    Args:
        server_address (tuple): (host, port) for server binding
        RequestHandlerClass: Class to handle HTTP requests
        chatbot (OpenAIChatBot): Chatbot instance for processing queries
        html_template_filepath (str): Path to HTML template file
        css_template_filepath (str): Path to CSS template file  
        js_template_filepath (str): Path to JavaScript template file
    """
    def __init__(self, server_address, RequestHandlerClass, chatbot,
                 html_template_filepath, css_template_filepath, js_template_filepath):
        
        super().__init__(server_address, RequestHandlerClass)
        RequestHandlerClass.set_chatbot(chatbot)
        RequestHandlerClass.set_html_template(read_template(html_template_filepath))
        RequestHandlerClass.set_css_template(read_template(css_template_filepath))
        RequestHandlerClass.set_js_template(read_template(js_template_filepath))
    
    def serve_forever(self, public=False):
        """
        Start the HTTP server with optional public tunnel.
        
        Args:
            public (bool): If True, creates ngrok tunnel for public access
            
        Note:
            Prints both local and public addresses when public=True
            Handles KeyboardInterrupt for graceful shutdown
        """
        print(f'Local Address:\t{self.get_local_address()}')
        if public:
            print(f'Public Address:\t{self.get_public_address()}', end='\n\n')
        try:
            with self:
                super().serve_forever()
        except KeyboardInterrupt:
            print('Keyboard interrupt received.\nServer stopping...')
    
    def get_local_address(self):
        """
        Get the local network address for the server.
        
        Returns:
            str: Local HTTP address in format 'http://IP:PORT'
            
        Note:
            Attempts to find the actual local IP, falls back to localhost
        """
        port = self.server_address[1]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
                return f'http://{local_ip}:{port}'
        except OSError:
            hostname = socket.gethostname()
            all_ips  = socket.getaddrinfo(hostname, None, socket.AF_INET)
            for info in ip_infos:
                local_ip = info[4][0]
                if not local_ip.startswith('127.'):
                    return f'http://{local_ip}:{port}'
        return f'http://127.0.0.1:{port}'
    
    def get_public_address(self):  # OPTIONAL -- for publicly accessible endpoints via an HTTP tunnel with a TLS layer
        """
        Create and get public ngrok tunnel address.
        
        Returns:
            str: Public HTTPS URL provided by ngrok
            
        Note:
            Requires pyngrok to be installed
            Creates a TLS-enabled tunnel for secure public access
        """
        from pyngrok import ngrok
        
        https_tunnel = ngrok.connect(self.server_address[1], bind_tls=True)
        return https_tunnel.public_url
