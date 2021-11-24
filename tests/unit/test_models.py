import pytest
from werkzeug.security import check_password_hash
from project.models import Site, User


@pytest.fixture(scope="module")
def test_user(test_database):
    user = User(username="User", password="password")
    test_database.session.add(user)
    test_database.session.commit()
    yield user


@pytest.fixture(scope="module")
def test_site(test_database, test_user):
    site = Site(
        user=test_user, url="test.com", title="Title", scrapping_time=123
    )
    test_database.session.add(site)
    test_database.session.commit()
    yield site


def test_add_user(test_database, test_user):
    assert test_user.username == "User"
    assert check_password_hash(test_user.password, "password")


def test_add_site(test_database, test_site):
    assert test_site.user.id == 1
    assert test_site.url == "test.com"
    assert test_site.title == "Title"
    assert test_site.scrapping_time == 123
    assert test_site.user.username == "User"
