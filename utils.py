import logging
from time import time

class Timer:
    
    def __enter__(self):
        self._start = self._time_ms()
        return self
    
    def __exit__(self, *args):
        self._elapsed = self._time_ms() - self._start

    def _time_ms(self):
        return round(1e3 * time())
    
    @property
    def start(self):
        return self._start
    
    @property
    def elapsed(self):
        return self._elapsed


def read_task_template(filepath):
    try:
        file = open(filepath)
        return file.read()
    except FileNotFoundError:
        message = 'LLM task description template not found!'
        logging.exception(message)
        print(f'{message}\nKindly check the error logs for traceback details.')
    finally:
        file.close()