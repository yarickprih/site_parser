import pytest
from flask_login import login_user
from werkzeug.security import check_password_hash
from project.models import User


@pytest.fixture(scope="module")
def test_user(app, _db):
    with app.app_context():
        user = User(username="User", password="password")
        _db.session.add(user)
        _db.session.commit()
        return user


@pytest.fixture(scope="module")
def logged_in_user(test_user):
    login_user(test_user)


def test_user_create(client, test_user):
    assert test_user.username == "User"
    assert check_password_hash(test_user.password, "password")
