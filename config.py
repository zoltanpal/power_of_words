import contextlib
import os

from dotenv import load_dotenv

from app.models.db_config import DBConfig

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "app")
STATIC_DIR = os.path.join(APP_DIR, "static")
VIEWS_DIR = os.path.join(APP_DIR, "views")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
DATA_DIR = os.path.join(ROOT_DIR, "data")

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

with contextlib.suppress(FileNotFoundError):
    dotenv_path = os.path.join(ROOT_DIR, ".env")
    load_dotenv(dotenv_path)

DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

pow_db_config = DBConfig(dialect='postgresql',
                         username=os.getenv("PSQL_USER", default="root"),
                         password=os.getenv("PSQL_PASSWORD", default="my_secret_password"),
                         dbname="power_of_words",
                         host=os.getenv("PSQL_HOST", default="localhost"),
                         port=int(os.getenv("PSQL_PORT", default=5432)))

POW_DB_CONFIG = {
    "user": os.getenv("PSQL_USER", default="root"),
    "password": os.getenv("PSQL_PASSWORD", default="my_secret_password"),
    "dbname": "power_of_words",
    "host": os.getenv("PSQL_HOST", default="localhost"),
    "port": int(os.getenv("PSQL_PORT", default=5432)),
    "minconn": 1,
    "maxconn": 10
}


pow_db_config_str = f'postgresql+psycopg2://{pow_db_config.username}:{pow_db_config.password}@{pow_db_config.host}/{pow_db_config.dbname}'

# TODO: should fetch from DB
SOURCES = {
    1: "444.hu",
    2: "telex.hu",
    3: "24.hu",
    4: "origo.hu",
    5: "hirado.hu",
    6: "magyarnemzet.hu",
    7: "index.hu",
  }
