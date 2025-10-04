import os
import sqlite3
import logging
import sys

def create_sqlite_db(db_filepath, scriptpath):
    """
    Create a SQLite database and execute SQL script to populate it.
    
    This function creates a new SQLite database file and executes all SQL commands
    from the provided script file to set up the database schema and initial data.
    
    Args:
        db_filepath (str): Path where the SQLite database file should be created
        scriptpath (str): Path to the SQL script file containing database setup commands
        
    Raises:
        Exception: Any exception encountered during database creation or script execution
        will be caught and logged, but not re-raised to the caller.
        
    Note:
        The function automatically handles database connection lifecycle and ensures
        the connection is properly closed even if errors occur.
    """
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
    """
    Main execution function for SQLite database creation utility.
    
    This function:
    1. Parses command line arguments for data handle and SQL script path
    2. Sets up directory structure for the database
    3. Removes existing database file if present
    4. Creates new database using the provided SQL script
    
    Command Line Usage:
        python script.py <DATA_HANDLE> <SQLITE_CMDS_PATH>
        
    Example:
        python script.py my_database setup.sql
        
    The database will be created at: ./data/<DATA_HANDLE>/data.sqlite
    
    Args:
        None - uses sys.argv for command line arguments
        
    Raises:
        SystemExit: If incorrect number of command line arguments provided
    """
    if len(sys.argv) < 3:
        print('Error: Incorrect number of arguments provided\nUsage: python script.py <DATA_HANDLE> <SQLITE_CMDS_PATH>')
        sys.exit(1)
            
    DATA_HANDLE = sys.argv[1]
    DB_DIRPATH  = os.path.abspath(f'./data/{DATA_HANDLE}')
    DB_FILEPATH = os.path.join(DB_DIRPATH, 'data.sqlite')
    SQLITE_CMDS = sys.argv[2]
    
    if os.path.isfile(DB_FILEPATH):
        os.remove(DB_FILEPATH)
    os.makedirs(DB_DIRPATH, exist_ok=True)
    create_sqlite_db(DB_FILEPATH, SQLITE_CMDS)
    print(f'\nProcess exited normally!')
    sys.exit(0)

if __name__ == '__main__':
    """
    Script entry point when executed directly.
    
    This module can be run as a standalone script to create SQLite databases
    from SQL command files. It requires two command line arguments:
    
    Required Arguments:
        sys.argv[1]: DATA_HANDLE - Unique identifier for the database
        sys.argv[2]: SQLITE_CMDS - Path to SQL script file
        
    The script will create the database in ./data/<DATA_HANDLE>/data.sqlite
    """
    main()