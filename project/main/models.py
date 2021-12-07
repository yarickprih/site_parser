import typing as t
from datetime import datetime

from flask import flash
from flask_login import UserMixin
from flask_login.utils import logout_user
from flask_sqlalchemy import BaseQuery
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from project import db, login

from .errors import EmptyQueryError


class DBModelMixin:
    """Mixin class implementing logic of adding
    entity to db and committing changes."""

    def commit_to_db(self) -> t.NoReturn:
        """Add instance to database session and commit it.

        Returns:
            NoReturn
        """
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
        default=datetime.utcnow,
    )
    last_login = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
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
            bool: bool value indicating whether passed
            password matched password hash of not
        """
        return check_password_hash(self.password, password)

    @classmethod
    def create(cls, **kwargs) -> None:
        """Create User instance with given parameters.

        Raises:
            e (IntegrityError): User already exists.

        Returns:
            None
        """
        try:
            user = cls(**kwargs)
            user.commit_to_db()
        except IntegrityError as e:
            raise e

    @classmethod
    def logout(cls, username: str) -> None:
        """Logout a user by the username.
        Additionally update logged out users last_login field.

        Args:
            username (str): Username of a user to logout.

        Returns:
            None
        """
        user = cls.query.filter_by(username=username).first()
        user.last_login = datetime.utcnow()
        user.commit_to_db()
        logout_user()


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
        unique=True,
    )
    title = db.Column(
        db.Text,
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    scrapping_time = db.Column(
        db.Integer,
        nullable=False,
    )

    @classmethod
    def get_by_url(cls, url: str) -> BaseQuery:
        """Get Site DB records queryset by given url.

        Args:
            url (str): Site url filter by field

        Raises:
            EmptyQueryError: No records found

        Returns:
            BaseQuery: SQLAlchemy queryset containing Site records
        """
        obj = cls.query.filter_by(url=url)
        if not obj.count():
            raise EmptyQueryError(
                f"Empty query. Site with url {url} doesn't exist"
            )
        return obj

    @classmethod
    def get_by_user(cls, user: User) -> t.List["Site"]:
        """Get Site DB records filtered by user field.

        Args:
            user (User): User instance

        Returns:
            List[Site]: List of Site instances filtered by passed user field.
        """
        return cls.query.filter_by(user=user).all()

    @classmethod
    def update_or_create(cls, data: t.Dict[str, t.Any]) -> None:
        """Update existing Site instance, create new one if not exists.

        Args:
            data (t.Dict[str, t.Any]): [description]
        """
        try:
            cls.get_by_url(data["url"]).update(
                dict(
                    user_id=data["user"].id,
                    scrapping_time=data["scrapping_time"],
                    created_at=data["created_at"],
                )
            )
        except EmptyQueryError:
            new_site = cls(**data)
            db.session.add(new_site)
