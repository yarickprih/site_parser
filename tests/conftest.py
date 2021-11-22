import pytest
from project import create_app, db


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.from_object("project.config.TestingConfig")
    with app.app_context():
        yield app


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def test_database(app):
    db.create_all()
    yield db  # testing happens here
    db.session.remove()
    db.drop_all()
