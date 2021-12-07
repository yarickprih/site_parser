import logging
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


def initialize_extensions(app: Flask) -> Flask:
    """Initialize application extentions.

    Args:
        app (Flask): Flask app instance

    Returns:
        Flask: Flask app instance with initialized extentions
    """
    db.init_app(app)
    login.init_app(app)
    login.login_view = "main_app.login_view"
    csrf.init_app(app)
    migrate.init_app(app, db)

    return app


def register_blueprints(app: Flask) -> None:
    from .main.routes import main_blueprint

    app.register_blueprint(main_blueprint)


def set_logger(app: Flask) -> None:
    """Set application logger.
    Set logger handler, configure logger and assign it
    to the Flask app.

    Args:
        app (Flask): Flask app instance
    """
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


def create_app(config: str = "dev") -> Flask:
    """Create Flask app factory.

    Args:
        config (str, optional): String representation of config_map key
        referencing config class. Defaults to "dev".

    Returns:
        Flask: initialized Flask application with
        all extentions connected and config set
    """
    app = Flask(__name__)
    app.config.from_object(config_map[config])
    set_logger(app)
    initialize_extensions(app)
    with app.app_context():
        register_blueprints(app)
    return app
