import pytest
from project import create_app, db


@pytest.fixture(scope="module")
def app():
    app = create_app()
    with app.app_context():
        app.config.from_object("project.config.TestingConfig")
        yield app


@pytest.fixture(scope="module")
def test_database(app):
    db.create_all()
    yield db
    db.drop_all()
