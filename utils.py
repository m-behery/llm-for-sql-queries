import logging
from time import time
import sqlite3

class Timer:
    """
    A context manager for measuring execution time in milliseconds.
    
    This class provides a simple way to time code blocks using Python's
    context manager protocol. It captures the start time when entering
    the context and calculates elapsed time when exiting.
    
    Attributes:
        _start (float): Start time in milliseconds when context is entered
        _elapsed (float): Elapsed time in milliseconds when context is exited
        
    Example:
        >>> with Timer() as timer:
        ...     # Some time-consuming operation
        ...     time.sleep(1)
        >>> print(f"Operation took {timer.elapsed} ms")
        Operation took 1000 ms
    """
    def __enter__(self):
        """
        Start the timer when entering the context.
        
        Returns:
            Timer: The timer instance itself for access to timing properties
        """
        self._start = self._time_ms()
        return self
    
    def __exit__(self, *args):
        """
        Stop the timer and calculate elapsed time when exiting the context.
        
        Args:
            *args: Exception information (ignored in this implementation)
        """
        self._elapsed = self._time_ms() - self._start

    def _time_ms(self):
        """
        Get current time in milliseconds.
        
        Returns:
            float: Current timestamp in milliseconds
        """
        return round(1e3 * time())
    
    @property
    def start(self):
        """
        Get the start time of the timer.
        
        Returns:
            float: Start time in milliseconds
        """
        return self._start
    
    @property
    def elapsed(self):
        """
        Get the elapsed time since the timer started.
        
        Returns:
            float: Elapsed time in milliseconds
        """
        return self._elapsed


def read_template(filepath: str):
    """
    Read and return the contents of a template file.
    
    This function safely reads a template file from the filesystem and returns
    its contents as a string. It handles file operations with proper exception
    handling and resource cleanup.
    
    Args:
        filepath (str): Path to the template file to read
        
    Returns:
        str: Contents of the template file, or None if file not found
        
    Raises:
        FileNotFoundError: If the specified file does not exist (handled internally)
        
    Example:
        >>> template = read_template('./templates/email_template.md')
        >>> print(f"Template length: {len(template)} characters")
    """
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
    """
    Execute a SQL query on a SQLite database with automatic connection management.
    
    This function provides a safe way to execute SQL queries on a SQLite database
    with proper transaction handling, connection lifecycle management, and
    automatic rollback on errors.
    
    Args:
        db_filepath (str): Path to the SQLite database file
        sqlite_query (str): SQL query to execute
        params (tuple, optional): Parameters for parameterized queries. Defaults to empty tuple.
        
    Returns:
        list or None: For SELECT/READ queries: list of result rows
                     For WRITE queries: None
                     On error: None
        
    Note:
        - Automatically detects if a query is a READ operation (SELECT, WITH, PRAGMA, EXPLAIN)
          or a WRITE operation (INSERT, UPDATE, DELETE, etc.)
        - READ operations return fetched results
        - WRITE operations commit changes and return None
        - All operations are wrapped in proper transaction handling with rollback on errors
        
    Example:
        >>> # Read operation
        >>> users = query_db('app.db', 'SELECT * FROM users WHERE age > ?', (18,))
        >>> # Write operation  
        >>> query_db('app.db', 'INSERT INTO users (name, age) VALUES (?, ?)', ('John', 25))
    """
    conn, rows = None, []
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
    """
    Extract the complete database schema from a SQLite database.
    
    This function queries the SQLite system tables to retrieve the CREATE TABLE
    statements for all user tables in the database, providing a complete
    schema definition.
    
    Args:
        db_filepath (str): Path to the SQLite database file
        
    Returns:
        str: A string containing all CREATE TABLE statements joined by newlines,
             suitable for documentation or schema replication.
             
    Example:
        >>> schema = extract_db_schema('my_database.db')
        >>> print(schema)
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT);
        
    Note:
        Only extracts tables (type='table'), excluding indexes, views, and other
        database objects. System tables like sqlite_sequence are automatically
        filtered out by the query.
    """
    rows = query_db(
        db_filepath,
        'SELECT sql FROM sqlite_master WHERE type="table";'
    )
    create_table_cmds = list(zip(*rows))[0]
    db_schema = '\n'.join(create_table_cmds)
    return db_schema