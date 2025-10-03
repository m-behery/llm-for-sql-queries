import sys

from chatbots import OpenAIChatBot
from http_service import Server, RequestHandler
from constants import ENVIRONMENT, FILEPATHS, CONNECTION_PARAMS

def main():
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

if __name__ == '__main__':
    main()
