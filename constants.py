import keyring
from argparse import Namespace

class ConstantNamespace(Namespace):
    """
    A read-only namespace for storing constant values.
    
    This class extends argparse.Namespace to create an immutable namespace
    where values can only be set once during initialization. Any attempt to
    modify existing attributes or add new ones after initialization will
    raise a NotImplementedError.
    
    Inherits from:
        argparse.Namespace: Provides basic namespace functionality
        
    Raises:
        NotImplementedError: When attempting to set or modify attributes
                           after initial initialization
                           
    Example:
        >>> constants = ConstantNamespace(API_KEY='123', HOST='localhost')
        >>> constants.API_KEY = '456'  # This will raise NotImplementedError
    """
    def __setattr__(self, name, value):
        """
        Override attribute setting to enforce immutability.
        
        Args:
            name (str): The name of the attribute to set
            value (any): The value to assign to the attribute
            
        Raises:
            NotImplementedError: If the attribute already exists or if trying
                               to set a new attribute after initialization
        """
        if name not in self.__dict__:
            self.__dict__[name] = value
            return
        raise NotImplementedError('This is a constant namespace.')

"""
Immutable namespace containing file paths for application resources.

This namespace stores all file system paths used by the application,
ensuring consistent access to templates, databases, and static assets.

Attributes:
    LLM_TASK_TEMPLATE (str): Path to the LLM task template markdown file
    HTML_TEMPLATE (str): Path to the main HTML template file
    CSS_TEMPLATE (str): Path to the CSS stylesheet file
    JS_TEMPLATE (str): Path to the JavaScript file
    MESSAGE_LOGS_DB (str): Path to the SQLite database for conversation logs
    
Example:
    >>> FILEPATHS.LLM_TASK_TEMPLATE
    './templates/llm_task_template.md'
"""
FILEPATHS = ConstantNamespace(
    LLM_TASK_TEMPLATE = './templates/llm_task_template.md',
    HTML_TEMPLATE     = './templates/template.html',
    CSS_TEMPLATE      = './templates/style.css',
    JS_TEMPLATE       = './templates/script.js',
    MESSAGE_LOGS_DB   = './conversations.db',
)

"""
Immutable namespace containing API credentials and environment settings.

This namespace stores configuration for AI providers, API endpoints,
model selection, and timing parameters. Sensitive data like API keys
are retrieved securely from the system keyring.

Attributes:
    PROVIDER (str): AI provider name (e.g., 'openai')
    OPENAI_API_KEY (str): OpenAI API key retrieved from system keyring
    OPENAI_CHAT_ENDPOINT (str): OpenAI API endpoint for chat completions
    MODEL_NAME (str): Name of the AI model to use (e.g., 'gpt-4o-mini')
    DELAY_MS (int): Delay in milliseconds between API calls to prevent rate limiting
    
Note:
    OPENAI_API_KEY is securely retrieved using keyring.get_password('openai', 'default')
    Ensure the API key is stored in the system keyring before running the application
    
Example:
    >>> ENVIRONMENT.MODEL_NAME
    'gpt-4o-mini'
"""
ENVIRONMENT = ConstantNamespace(
    PROVIDER             = 'openai',
    OPENAI_API_KEY       = keyring.get_password('openai', 'default'),
    OPENAI_CHAT_ENDPOINT = 'https://api.openai.com/v1/chat/completions',
    MODEL_NAME           = 'gpt-4o-mini',
    DELAY_MS             = 2500, # To make sure we don't get blocked from the 2nd subsequent call to translate the SQL result to natural language
)

"""
Immutable namespace containing server connection parameters.

This namespace stores network configuration for the web server including
host binding, port allocation, and deployment settings.

Attributes:
    HOST (str): Host address to bind the server to ('0.0.0.0' for all interfaces)
    PORT (int): Port number for the server to listen on
    PUBLIC (bool): Flag indicating whether to enable public access via HTTP tunnel
    
Note:
    When PUBLIC is True, the application can be deployed with remote access
    capabilities including TLS-secured HTTP tunneling for secure remote deployment.
    
Example:
    >>> CONNECTION_PARAMS.PORT
    8000
"""
CONNECTION_PARAMS = ConstantNamespace(
    HOST = '0.0.0.0',
    PORT = 8000,
    PUBLIC = True,  # OPTIONAL -- for publicly accessible endpoints via an HTTP tunnel with a TLS layer
)