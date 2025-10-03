import logging
from time import time
import sqlite3

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


def read_template(filepath: str):
    try:
        file = open(filepath)
        return file.read()
    except FileNotFoundError:
        message = 'Template not found!'
        logging.exception(message)
        print(f'{message}\nKindly check the error logs for traceback details.')
    finally:
        file.close()


def query_db(db_filepath: str, sqlite_query: str, params: tuple=tuple()):
    rows = None
    conn = None
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(sqlite_query, params)
        
        query_lower = sqlite_query.lower().strip()
        is_fetch = any(
            query_lower.startswith(verb) for verb in {'select', 'with', 'pragma', 'explain'}
        )
        
        if is_fetch:
            rows = cursor.fetchall()
        else:
            conn.commit()
    except:
        logging.exception('Database Error.\nKindly check the error logs for traceback details.')
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return rows


def extract_db_schema(db_filepath: str):
    rows = query_db(
        db_filepath,
        'SELECT sql FROM sqlite_master WHERE type="table";'
    )
    create_table_cmds = list(zip(*rows))[0]
    db_schema = '\n'.join(create_table_cmds)
    return db_schema