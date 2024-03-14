import os
from decouple import Config, RepositoryEnv

BASE_DIR = os.getcwd()
DOTENV_FILE = os.path.join(BASE_DIR, '.env')

config = Config(RepositoryEnv(DOTENV_FILE))

## PostgreSQL database ##
DATABASE = config('DATABASE')
POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
HOST = config('HOST')
DOCKER_POSTGRES_HOST = config('DOCKER_POSTGRES_HOST')
PORT = config('PORT')

## Adzuna API ##
API_KEY = config('API_KEY')
API_ID = config('API_ID')


## Data to ingest folder ##
DATA_TO_INGEST_FOLDER = os.path.join(BASE_DIR, 'postgresql', 'data_to_ingest')