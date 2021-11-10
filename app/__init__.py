from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import DevelopmentConfig

ma = Marshmallow()
db = SQLAlchemy()
migrate = Migrate()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    initialize_extensions(app)
    return app


def initialize_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    from .models import User, Site

    return app


if __name__ == "__main__":
    app = create_app("dev")
    app.run()
