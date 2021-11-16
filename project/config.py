import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent


def create_db_url() -> str:
    """Generate database URL.

    Returns:
        str: database URL string
    """
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    """Base app config class."""

    DEBUG = bool(os.getenv("DEBUG", "0"))
    SECRET_KEY = str(os.getenv("SECRET_KEY", "secret_key"))
    SQLALCHEMY_DATABASE_URI = create_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FILES_DIR = PROJECT_DIR / "files"
    LINKS_FILE = BASE_DIR / "links.txt"


class ProductionConfig(Config):
    """Production config class (inherited from base config class)"""

    DEBUG = False


class DevelopmentConfig(Config):
    """Development config class (inherited from base config class)"""

    DEBUG = True


class TestingConfig(Config):
    """Testing config class (inherited from base config class)"""

    TESTING = True


config_map = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
