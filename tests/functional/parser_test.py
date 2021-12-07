from project.main.models import Site


def test_commit_parsed(app, client, test_database, test_user, test_all_sites):
    from project.main.parser import commit_parsed

    # commit_parsed(test_user, app.config["UPLOADS"] / "links.txt")
    # path = app.config["UPLOADS"] / "links.txt"
    # file = path.read_text().split("\n")[:-1]
    # for site in Site.query.all():
    #     assert site.url in file
