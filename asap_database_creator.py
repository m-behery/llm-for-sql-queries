import os
import sqlite3
import logging
import sys

def create_sqlite_db(db_filepath, scriptpath):
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        with open(scriptpath) as f:
            script = f.read()
        cursor.executescript(script)
        print(f'Database created successfully!\n\nDatabase File:\n{db_filepath}')
    except Exception as e:
        message = 'Error while creating database!'
        logging.exception(message)
        print(f'{message}\nKindly check the error logs for traceback details.')
    finally:
        conn.close()

def main():
    
    DATA_HANDLE = sys.argv[1]
    DB_DIRPATH  = os.path.abspath(f'./data/{DATA_HANDLE}')
    DB_FILEPATH = os.path.join(DB_DIRPATH, 'data.sqlite')
    SQLITE_CMDS = sys.argv[2]
    
    if os.path.isfile(DB_FILEPATH):
        os.remove(DB_FILEPATH)
    os.makedirs(DB_DIRPATH, exist_ok=True)
    create_sqlite_db(DB_FILEPATH, SQLITE_CMDS)

if __name__ == '__main__':
    main()