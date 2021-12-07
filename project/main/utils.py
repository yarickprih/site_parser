import random
import typing as t
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from functools import wraps
from pathlib import Path, PosixPath
from threading import Thread
from typing import List
from xml.dom import minidom

from bs4 import BeautifulSoup
from faker import Faker
from flask import current_app as app
from flask import flash, redirect, url_for
from flask_login import current_user

from .models import Site, User

fake = Faker()


def create_xml_report(urls: List[Site]) -> str:
    """Create an XML report file.

    Creates an XML report file with info
    on a list of Site database model instances

    Args:
        urls (List[Site]): List of Site database model instances

    Returns:
        str: Created XML report file name
    """
    if not urls:
        raise ValueError("Empty urls list")
    root = ET.Element("Catalog")

    for url in urls:
        site = ET.Element("site")
        root.append(site)

        title = ET.SubElement(site, "title")
        url_str = ET.SubElement(site, "url")
        user = ET.SubElement(site, "user")
        scrapping_time = ET.SubElement(site, "scrapping_time")
        date = ET.SubElement(site, "date")

        title.text = url.title
        url_str.text = url.url
        user.text = url.user.username
        scrapping_time.text = str(url.scrapping_time)
        date.text = url.created_at.strftime("%B %d %Y")

    tree = minidom.parseString(ET.tostring(root)).toprettyxml(indent=" " * 4)
    save_path = Path(app.config["FILES_DIR"])
    if not save_path.exists():
        save_path.mkdir(parents=True, exist_ok=True)
    file_name = f"{uuid.uuid4()}.xml"
    with open(f"{save_path}/{file_name}", "w") as file:
        file.write(tree)
    return file_name


def create_site_dict(
    user: User, url: str, data: str, time_: float
) -> t.Dict[str, t.Any]:
    """Create a dictionary of Site model attributes and values
    with passed arguments.

    Args:
        user (User): SQLAlchemy User model instance
        url (str): URL string
        data (str): URL page body
        time_ (float): Time in took to make a request

    Returns:
        Dict[str, Any]: dictionary with Site
        model attributes and values
    """
    soup = BeautifulSoup(data, "lxml")
    try:
        title = soup.select_one("title").text.strip()
    except AttributeError:
        title = "Unknown title"
    return dict(
        user=user,
        url=url[:-1],
        title=title,
        scrapping_time=int(time_ * 1000),
        created_at=datetime.utcnow(),
    )


def create_fake_user(instances: int = 1) -> List[User]:
    """Generate SQLAlchemy User model instance with fake data.

    Args:
        instances (int, optional): number of instances to create.
        Defaults to 1.

    Returns:
        List[User]: list of User model instances
    """
    user = User(
        username=fake.simple_profile()["username"],
        password=fake.password(length=12),
    )
    return [user for _ in range(instances)]


def create_fake_site(user: User, instances: int = 1) -> List[Site]:
    """Generate SQLAlchemy User model instance with fake data.

    Args:
        user (User): SQLAlchemy User model instance
        instances (int, optional): number of instances to create.
        Defaults to 1.

    Returns:
        List[Site]: list of Site model instances
    """
    site = Site(
        user=user,
        url=fake.url(),
        title=" ".join(fake.words(nb=random.randint(1, 10))),
        scrapping_time=random.randint(0, 10000),
    )
    return [site for _ in range(instances)]


def get_user_uploads_folder(user: User) -> PosixPath:
    """Create user uploads directory if corresponding one is missing.

    Check if user uploads folder exists and if not create it

    Args:
        user (User): User instance

    Returns:
        PosixPath: pathlib path to the user uploads folder
    """
    path = Path(app.config["UPLOADS"]) / user.username
    if not path.exists():
        Path.mkdir(path, parents=True, exist_ok=True)
    return path


def user_authenticated(func):
    """Check wether current user is authenticated.
    If current user is authenticated - redirect to
    the index page. If not - process route function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("main_app.index"))
        return func(*args, **kwargs)

    return wrapper


def flash_form_errors(form) -> None:
    """Flash form errors.
    Flash unprocessed errors that occurred while processing
    the form.

    Args:
        form: form instance
    """
    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
