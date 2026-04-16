import configparser
import os
from pathlib import Path

BASE_SOURCE_PATH = Path(os.path.dirname(__file__)).absolute().parent
config = configparser.ConfigParser()
config.read(f'{BASE_SOURCE_PATH}/config.ini', encoding='utf-8')

# [LOG]
LOG_FILE_PATH = config.get('LOG', 'LOG_FILE_PATH')

# [DB]
DB_HOST = config.get('DB', 'DB_HOST')
DB_PORT = config.get('DB', 'DB_PORT')
DB_USER = config.get('DB', 'DB_USER')
DB_PASSWORD = config.get('DB', 'DB_PASSWORD')
DB_NAME = config.get('DB', 'DB_NAME')

# [BACKEND]
BACKEND_HOST = config.get('BACKEND', 'BACKEND_HOST')
BACKEND_PORT = config.get('BACKEND', 'BACKEND_PORT')
