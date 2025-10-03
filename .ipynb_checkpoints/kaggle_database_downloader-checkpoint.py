import kagglehub
import shutil
import os
import sys

KAGGLE_HANDLE   = None
DATASET_DIRPATH = None
DB_EXT_KEYWORDS = ('sqlite', 'db')


def is_db(filepath, ext_keywords=DB_EXT_KEYWORDS):
    if os.path.isfile(filepath):
        ext = os.path.splitext(filepath)[-1]
        return any(x.lower().strip() in ext.lower().strip() for x in ext_keywords)
    return False


def find_db_filepath(dirpath, ext_keywords=DB_EXT_KEYWORDS):
    for name in os.listdir(DATASET_DIRPATH):
        path = os.path.join(DATASET_DIRPATH, name)
        if is_db(path, ext_keywords):
            return path
    raise FileNotFoundError('Database file not found given the following extension keywords {"sql", "db"}...')


def main():
    global KAGGLE_HANDLE, DATASET_DIRPATH
    
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


if __name__ == '__main__':
    status = main()
