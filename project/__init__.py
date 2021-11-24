import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from .config import config_map

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
    app.config.from_object(config_map[os.getenv("CONFIG", "dev")])
    initialize_extensions(app)
    with app.app_context():
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
