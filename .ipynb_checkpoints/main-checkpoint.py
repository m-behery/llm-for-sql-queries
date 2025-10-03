import sys

from chatbots import OpenAIChatBot
from http_service import Server, RequestHandler
from constants import ENVIRONMENT, FILEPATHS, CONNECTION_PARAMS

def main():
    """
    Main application entry point for the AI Chatbot SQL Assistant.
    
    This function initializes and starts the complete application stack:
    1. Creates an OpenAI chatbot instance with database integration
    2. Configures and starts an HTTP server with the chatbot
    3. Serves the web interface for user interactions
    
    Command Line Usage:
        python app.py <DATABASE_FILEPATH>
        
    Example:
        python app.py ./data/my_database.sqlite
        
    The application will start a web server accessible locally and optionally
    publicly via ngrok tunnel, providing a chat interface for natural language
    SQL queries against the specified database.
    
    Args:
        None - uses sys.argv for command line arguments
        
    Raises:
        SystemExit: If incorrect number of command line arguments provided
        FileNotFoundError: If the specified database file does not exist
        Exception: Various exceptions from chatbot or server initialization
        
    Note:
        Requires a valid SQLite database file path as command line argument
        OpenAI API key must be configured in the system keyring
        Server configuration is loaded from constants module
    """
    if len(sys.argv) < 2:
        print('Error: Database filepath argument required\nUsage: python app.py <DATABASE_FILEPATH>')
        sys.exit(1)
        
    db_filepath = sys.argv[1]
    chatbot = OpenAIChatBot(
        ENVIRONMENT.OPENAI_API_KEY,
        ENVIRONMENT.MODEL_NAME,
        FILEPATHS.LLM_TASK_TEMPLATE,
        db_filepath,
    )
    server = Server(
        (CONNECTION_PARAMS.HOST, CONNECTION_PARAMS.PORT), RequestHandler, chatbot,
        FILEPATHS.HTML_TEMPLATE, FILEPATHS.CSS_TEMPLATE, FILEPATHS.JS_TEMPLATE
    )
    server.serve_forever(CONNECTION_PARAMS.PUBLIC)
    print('\nProcess exited normally!')
    sys.exit(0)

if __name__ == '__main__':
    """
    AI Chatbot SQL Assistant - Main Application Module.
    
    This module serves as the entry point for the AI-powered SQL query assistant
    that allows users to interact with databases using natural language through
    a web interface.
    
    Application Architecture:
        - OpenAIChatBot: Handles natural language processing and SQL generation
        - Server: HTTP server serving the web interface and API endpoints
        - RequestHandler: Processes HTTP requests and routes to the chatbot
        - Constants: Centralized configuration from environment and file paths
        
    Features:
        - Natural language to SQL conversion
        - Database schema awareness
        - Web-based chat interface
        - Session logging and persistence
        - Optional public deployment via ngrok
        
    Prerequisites:
        - SQLite database file for querying
        - OpenAI API key configured in system keyring
        - Required Python packages installed
        - Network access for API calls and optional ngrok tunneling
        
    Configuration:
        All configuration is managed through the constants module:
        - ENVIRONMENT: API keys, model settings, and timing
        - FILEPATHS: Template and resource file locations  
        - CONNECTION_PARAMS: Server host, port, and deployment settings
    """
    main()
