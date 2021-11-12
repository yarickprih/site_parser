import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


def create_db_url() -> str:
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    DEBUG = bool(os.getenv("DEBUG", "0"))
    SECRET_KEY = str(os.getenv("SECRET_KEY", "secret_key"))
    SQLALCHEMY_DATABASE_URI = create_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config_map = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
