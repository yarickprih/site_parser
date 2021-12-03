import pytest
from werkzeug.security import check_password_hash
from project.main.errors import EmptyQueryError
from project.main.models import Site


class TestUser:
    def test_add_user(self, test_database, test_user):
        assert test_user.username == "User"
        assert check_password_hash(test_user.password, "password")


class TestSite:
    def test_add_site(self, test_database, test_site):
        assert test_site.user.id == 1
        assert test_site.url == "test.com"
        assert test_site.title == "Title"
        assert test_site.scrapping_time == 123
        assert test_site.user.username == "User"

    def test_site_get_by_url_valid(self, test_database, test_site):
        site = Site.get_by_url("test.com")
        assert site.count() == 1
        assert site.first() == test_site

    def test_site_get_by_url_invalid(self, test_database):
        with pytest.raises(EmptyQueryError) as exc:
            Site.get_by_url("invalid.com")
        assert "Empty query" in str(exc.value)

    def test_site_get_by_user_valid(self, test_database, test_site, test_user):
        site = Site.get_by_user(test_user)
        assert site[0].user.username == test_user.username
        assert len(site) > 0

    def test_site_get_by_user_invalid(
        self, test_database, test_site, test_fake_user
    ):
        site = Site.get_by_user(test_fake_user)
        assert len(site) == 0
