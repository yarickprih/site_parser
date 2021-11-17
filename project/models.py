from datetime import datetime
from typing import NoReturn

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from project import db, login


class DBModelMixin:
    """Mixin class implementing logic of adding entity to db and committing changes."""

    def commit_to_db(self) -> NoReturn:
        db.session.add(self)
        db.session.commit()


class User(db.Model, UserMixin, DBModelMixin):
    """Database User model."""

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
    last_login = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
    sites = db.relationship(
        "Site",
        cascade="all,delete",
        backref="user",
        lazy=True,
    )

    def __repr__(self) -> str:
        return str(
            {
                key: value
                for key, value in self.__dict__.items()
                if not key.startswith("_")
            }
        )

    def __setattr__(self, name, value):
        if name == "password":
            value = generate_password_hash(value)
        super().__setattr__(name, value)

    def check_password(self, password: str) -> bool:
        """Check if passed password matches instances password hash.

        Args:
            password (str): password string

        Returns:
            bool: bool value indicating whether passed password matched password hash of not
        """
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Site(db.Model, DBModelMixin):
    """Database Site model."""

    __tablename__ = "sites"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
    )
    url = db.Column(
        db.String(255),
        nullable=False,
    )
    title = db.Column(
        db.Text,
        nullable=False,
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

