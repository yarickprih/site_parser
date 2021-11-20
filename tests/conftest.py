import pytest
from project import create_app, db


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture(scope="session")
def app():
    _app = create_app()
    _app.config.from_object("project.config.TestingConfig")
    with _app.app_context():
        yield _app


@pytest.fixture(scope="session")
def _db(app):
    """
    Returns session-wide initialized database.
    """
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
