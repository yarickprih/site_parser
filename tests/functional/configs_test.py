from project.config import create_db_url, BASE_DIR


def test_testing_config(app):
    app.config.from_object("project.config.TestingConfig")
    assert app.config["TESTING"]
    assert app.config["DEBUG"]
    assert (
        app.config["SQLALCHEMY_DATABASE_URI"]
        == f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
    assert not app.config["WTF_CSRF_ENABLED"]


def test_development_config(app):
    app.config.from_object("project.config.DevelopmentConfig")
    assert not app.config["TESTING"]
    assert app.config["DEBUG"]
    assert app.config["SQLALCHEMY_DATABASE_URI"] == create_db_url()


def test_production_config(app):
    app.config.from_object("project.config.ProductionConfig")
    assert not app.config["DEBUG"]
    assert not app.config["TESTING"]
    assert app.config["SQLALCHEMY_DATABASE_URI"] == create_db_url()
