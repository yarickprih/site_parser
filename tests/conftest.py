import pytest
from flask.testing import FlaskClient
from project import create_app, db

pytest_plugins = ["tests.fixtures"]


@pytest.fixture(scope="module")
def app():
    app = create_app(config="test")
    with app.app_context():
        yield app


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def test_database(app):
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()
