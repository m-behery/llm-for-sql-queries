import keyring

DB_FILEPATH                = './data/aayman/asap-database-template/data.sqlite'
LLM_TASK_TEMPLATE_FILEPATH = './llm_task_template.md'

PROVIDER             = 'openai'
OPENAI_API_KEY       = keyring.get_password('openai', 'default')
OPENAI_CHAT_ENDPOINT = 'https://api.openai.com/v1/chat/completions'
MODEL_NAME           = 'gpt-4o-mini'