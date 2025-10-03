import keyring
from argparse import Namespace

class ConstantNamespace(Namespace):
    def __setattr__(self, name, value):
        if name not in self.__dict__:
            self.__dict__[name] = value
            return
        raise NotImplementedError('This is a constant namespace.')

FILEPATHS = ConstantNamespace(
    LLM_TASK_TEMPLATE = './templates/llm_task_template.md',
    HTML_TEMPLATE     = './templates/template.html',
    CSS_TEMPLATE      = './templates/style.css',
    JS_TEMPLATE       = './templates/script.js',
    MESSAGE_LOGS_DB   = './conversations.db',
)

ENVIRONMENT = ConstantNamespace(
    PROVIDER             = 'openai',
    OPENAI_API_KEY       = keyring.get_password('openai', 'default'),
    OPENAI_CHAT_ENDPOINT = 'https://api.openai.com/v1/chat/completions',
    MODEL_NAME           = 'gpt-4o-mini',
    DELAY_MS             = 0, # To make sure we don't get blocked from the 2nd subsequent call to translate the SQL result to natural language
)

CONNECTION_PARAMS = ConstantNamespace(
    HOST = '0.0.0.0',
    PORT = 8000,
    PUBLIC = True,  # BONUS -- for remote deployment via an HTTP tunnel with a TLS layer
)