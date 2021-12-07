import random
import shutil

import requests
from faker import Faker
from project.main.models import Site, User
from project.main.utils import (
    create_fake_site,
    create_fake_user,
    create_site_dict,
    create_xml_report,
    get_user_uploads_folder,
)

fake = Faker()


def test_create_xml_report(app, test_sites_list):
    report = create_xml_report(test_sites_list)
    with open(app.config["FILES_DIR"] / report, "r") as file:
        data = file.read()
        assert "Catalog" in data
        assert all(site.url in data for site in test_sites_list)
        assert all(site.user.username in data for site in test_sites_list)
        assert all(site.title in data for site in test_sites_list)
        assert all(
            str(site.scrapping_time) in data for site in test_sites_list
        )
    shutil.rmtree(app.config["FILES_DIR"])


def test_create_site_dict(test_user):
    url = "https://google.com"
    data = requests.get(url).text
    time = random.randint(1, 5000)
    result = create_site_dict(test_user, url, data, time)
    assert isinstance(result, dict)
    assert result["url"] == url[:-1]


def test_create_fake_user():
    users = create_fake_user(10)
    assert len(users) == 10
    assert all(isinstance(user, User) for user in users)
    assert all(user.username and user.password for user in users)


def test_create_fake_site(test_user):
    sites = create_fake_site(user=test_user, instances=10)
    assert len(sites) == 10
    assert all(isinstance(site, Site) for site in sites)
    assert all(site.user.username == test_user.username for site in sites)


def test_get_user_uploads_folder(app, test_user):
    path = get_user_uploads_folder(test_user)
    assert path == app.config["UPLOADS"] / test_user.username
    assert path.exists()
    shutil.rmtree(path)
