import kagglehub
import shutil
import os
import sys
from typing import final

DB_EXT_KEYWORDS: final = ('sqlite', 'db')


def is_db(filepath, ext_keywords=DB_EXT_KEYWORDS):
    """
    Check if a file is a database file based on its extension.
    
    This function examines the file extension to determine if it matches
    known database file extensions such as .sqlite, .db, etc.
    
    Args:
        filepath (str): Path to the file to check
        ext_keywords (tuple): Tuple of file extension keywords to match against.
                            Defaults to ('sqlite', 'db')
                            
    Returns:
        bool: True if the file extension matches any of the database keywords,
              False otherwise or if the path is not a file
              
    Example:
        >>> is_db('/path/to/database.sqlite')
        True
        >>> is_db('/path/to/data.csv')
        False
    """
    if os.path.isfile(filepath):
        ext = os.path.splitext(filepath)[-1]
        return any(x.lower().strip() in ext.lower().strip() for x in ext_keywords)
    return False


def find_db_filepath(dirpath, ext_keywords=DB_EXT_KEYWORDS):
    """
    Search a directory for database files and return the first match.
    
    This function scans the specified directory for files with database
    extensions and returns the path to the first database file found.
    
    Args:
        dirpath (str): Path to the directory to search for database files
        ext_keywords (tuple): Tuple of file extension keywords to match against.
                            Defaults to ('sqlite', 'db')
                            
    Returns:
        str: Absolute path to the first database file found
        
    Raises:
        FileNotFoundError: If no database files are found in the directory
        NotADirectoryError: If the provided path is not a directory
        
    Example:
        >>> find_db_filepath('/path/to/dataset')
        '/path/to/dataset/data.sqlite'
    """
    if not os.path.isdir(dirpath):
        raise NotADirectoryError(f'The directory path "{dirpath}" does not exist.')
    for name in os.listdir(dirpath):
        path = os.path.join(dirpath, name)
        if is_db(path, ext_keywords):
            return path
    raise FileNotFoundError('Database file not found given the following extension keywords {"sql", "db"}...')


def main():
    """
    Main function to download and process a Kaggle dataset.
    
    This function:
    1. Downloads a dataset from Kaggle using the provided handle
    2. Moves the dataset to a local data directory
    3. Locates and reports the database file within the dataset
    4. Cleans up any existing dataset directory before download
    
    Command Line Usage:
        python script.py <KAGGLE_DATASET_HANDLE>
        
    Example:
        python script.py username/dataset-name
        
    The dataset will be downloaded to: ./data/<KAGGLE_HANDLE>/
    
    Global Variables:
        Modifies KAGGLE_HANDLE and DATASET_DIRPATH global variables
        
    Returns:
        None
    """

    if len(sys.argv) < 2:
        print('Error: Incorrect number of arguments provided\nUsage: python script.py <KAGGLE_DATASET_HANDLE>')
        sys.exit(1)
    
    KAGGLE_HANDLE   = sys.argv[1]
    DATASET_DIRPATH = os.path.abspath(f'./data/{KAGGLE_HANDLE}')
    
    if os.path.isdir(DATASET_DIRPATH):
        shutil.rmtree(DATASET_DIRPATH)
    
    download_dirpath = kagglehub.dataset_download(
        handle=KAGGLE_HANDLE,
    )
    print(f'\nDataset downloaded to:\n"{download_dirpath}"')
    
    shutil.move(
        src=download_dirpath, 
        dst=DATASET_DIRPATH,
    )
    print(f'\nDataset moved to:\n"{DATASET_DIRPATH}"')
    
    DB_FILEPATH = find_db_filepath(DATASET_DIRPATH)
    print(f'\nDatabase File:\n"{DB_FILEPATH}"')
    
    print(f'\nProcess exited normally!')
    sys.exit(0)


if __name__ == '__main__':
    """
    Kaggle Dataset Downloader Script Entry Point.
    
    This script automates the process of downloading datasets from Kaggle
    and locating database files within them. It requires a Kaggle dataset
    handle as a command line argument.
    
    Prerequisites:
        - Kaggle API credentials configured (~/.kaggle/kaggle.json)
        - kagglehub package installed
        - Sufficient disk space for the dataset
        
    Required Command Line Argument:
        sys.argv[1]: KAGGLE_HANDLE - Kaggle dataset handle in format 'username/dataset-name'
        
    Example:
        python kaggle_downloader.py zillow/zecon
        
    The script will:
        1. Remove existing dataset directory if present
        2. Download the dataset using kagglehub
        3. Move dataset to ./data/<KAGGLE_HANDLE>/
        4. Identify and display the path to database files
    """
    status = main()
