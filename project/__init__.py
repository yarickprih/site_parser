import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from .config import BASE_DIR, config_map

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()


def create_app() -> Flask:
    """Create Flask app factory.

    Returns:
        Flask: initialized Flask application with
        all extentions connected and config set
    """
    app = Flask(__name__)
    set_logger(app)
    app.config.from_object(config_map[os.getenv("CONFIG", "dev")])
    with app.app_context():
        initialize_extensions(app)
        from . import routes
        from .models import Site, User

        return app


def initialize_extensions(app: Flask) -> Flask:
    """Initialize application extentions.

    Args:
        app (Flask): Flask app instance

    Returns:
        Flask: Flask app instance with initialized extentions
    """
    db.init_app(app)
    login.init_app(app)
    login.login_view = "login"
    csrf.init_app(app)
    migrate.init_app(app, db)

    return app


def set_logger(app: Flask) -> None:
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    )
    handler = RotatingFileHandler(
        BASE_DIR / "logs.txt",
        maxBytes=10000000,
        backupCount=5,
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
