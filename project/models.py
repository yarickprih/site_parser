from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from project import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    username = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )
    password = db.Column(
        db.String(128),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=db.func.current_timestamp(),
    )
    modified_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
    sites = db.Column(db.ForeignKey("sites.id"))

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __setattr__(self, name, value):
        if name == "password":
            value = generate_password_hash(value)
        super().__setattr__(name, value)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Site(db.Model):
    __tablename__ = "sites"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id = db.relationship(
        "User",
        backref="site",
        lazy=True,
    )
    url = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )
    title = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.now(),
    )
    scrapping_time = db.Column(
        db.Integer,
        nullable=False,
    )
