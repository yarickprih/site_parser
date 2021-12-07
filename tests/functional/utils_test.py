import shutil

from faker import Faker
from project.main.utils import create_xml_report

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


# def test_create_site_dict()
