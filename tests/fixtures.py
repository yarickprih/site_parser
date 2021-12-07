import random

import pytest
from faker import Faker
from flask_login import login_user
from project import db
from project.main.models import Site, User
from project.main.utils import create_fake_user

fake = Faker()


@pytest.fixture(scope="module")
def test_all_sites(test_database):
    yield Site.query.all()


@pytest.fixture(scope="module")
def test_fake_user(test_database):
    user = create_fake_user()[0]
    user.commit_to_db()
    yield user


@pytest.fixture(scope="module")
def test_fake_site(test_database, test_fake_user):
    site = {
        "user": test_fake_user,
        "url": fake.url(),
        "title": " ".join(fake.words(nb=random.randint(1, 10))),
        "scrapping_time": random.randint(0, 10000),
    }
    yield site


@pytest.fixture(scope="module")
def test_site(test_database, test_user):
    site = Site(
        user=test_user,
        url="test.com",
        title="Title",
        scrapping_time=123,
    )
    site.commit_to_db()
    yield site


@pytest.fixture(scope="module")
def test_user(test_database):
    user = User(
        username="User",
        password="password",
    )
    user.commit_to_db()
    yield user


@pytest.fixture(scope="module")
def logged_in_user(test_user):
    login_user(test_user)
    yield test_user


@pytest.fixture(scope="module")
def test_sites_list(app, test_user):
    sites = [
        Site(
            user=test_user,
            url=fake.url(),
            title=" ".join(fake.words(nb=random.randint(1, 10))),
            scrapping_time=random.randint(0, 10000),
        )
        for _ in range(10)
    ]
    db.session.add_all(sites)
    yield sites
