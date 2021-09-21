import os
import sys
from app import dotenv_path
from dotenv import load_dotenv

load_dotenv(dotenv_path)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Set Flask configuration vars from .env file."""

    FLASK_ENV = os.getenv("FLASK_ENV")

    DB_ENGINE = os.getenv("DB_ENGINE", default="POSTGRES")

    # SQL database
    SQL_DB_USER = os.getenv("DB_USER")
    SQL_DB_HOST = ""
    SQL_DB_NAME = os.getenv("DB_NAME")
    SQL_DB_PASSWORD = os.getenv("DB_PASSWORD")
    SQL_DB_PORT = os.getenv("DB_PORT", default=5432)

    # MONGO database
    MONGODB_DB = os.getenv("DB_NAME")
    MONGODB_PORT = int(os.getenv("DB_PORT", default=27017))
    MONGODB_USERNAME = os.getenv("DB_USER")
    MONGODB_PASSWORD = os.getenv("DB_PASSWORD")
    MONGODB_CONNECT = False

    # REDIS
    REDIS_SERVER = os.getenv("REDIS_SERVER")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    # General
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = "SECRET"
    FLASK_RUN_PORT = 6000
    TESTING = False
    LOGFILE = "log.log"
    APP_NAME = "distributor"

    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", default="localhost:9092"
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return "postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}".format(  # noqa
            db_user=self.SQL_DB_USER,
            host=self.SQL_DB_HOST,
            password=self.SQL_DB_PASSWORD,
            port=self.SQL_DB_PORT,
            db_name=self.SQL_DB_NAME,
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQL_DB_HOST = os.getenv("DEV_DB_HOST", default="localhost")
    MONGODB_HOST = os.getenv("DEV_DB_HOST", default="localhost")
    LOG_BACKTRACE = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    SQL_DB_HOST = os.getenv("DB_HOST")
    MONGODB_HOST = os.getenv("DB_HOST")
    LOG_BACKTRACE = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    DB_NAME = "test"
    TESTING = True
    DEBUG = True
    DEVELOPMENT = True
    LOG_BACKTRACE = True
    LOG_LEVEL = "DEBUG"
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(basedir, DB_NAME) + ".db?check_same_thread=False"
    )
