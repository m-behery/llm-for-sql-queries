import keyring
from argparse import Namespace

class ConstantNamespace(Namespace):
    def __setattr__(self, name, value):
        if name not in self.__dict__:
            self.__dict__[name] = value
            return
        raise NotImplementedError('This is a constant namespace.')

FILEPATHS = ConstantNamespace(
    DATABASE = './data/aayman/asap-database-template/data.sqlite',
    LLM_TASK_TEMPLATE = './llm_task_template.md',
)

ENVIRONMENT = ConstantNamespace(
    PROVIDER             = 'openai',
    OPENAI_API_KEY       = keyring.get_password('openai', 'default'),
    OPENAI_CHAT_ENDPOINT = 'https://api.openai.com/v1/chat/completions',
    MODEL_NAME           = 'gpt-4o-mini',
    DELAY_MS             = 2500, # To make sure we don't get blocked from the 2nd subsequent call to translate the SQL result to natural language
)

CONNECTION_PARAMS = ConstantNamespace(
    HOST = '0.0.0.0',
    PORT = 8000,
    PUBLIC = True,  # BONUS -- for remote deployment via an HTTP tunnel with a TLS layer
)