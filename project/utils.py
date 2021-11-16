import random
import uuid
import xml.etree.ElementTree as ET
from functools import wraps
from pathlib import Path
from typing import Callable, List
from xml.dom import minidom

from faker import Faker
from flask import current_app as app

from .config import Config
from .models import Site, User

fake = Faker()


def create_xml_report(urls: List[Site]) -> str:
    """This function takes a list of Site database model instances
    and creates an XML report file with info on every Site.

    Args:
        urls (List[Site]): List of Site database model instances

    Returns:
        str: Created XML report file name
    """
    root = ET.Element("Catalog")

    for url in urls:
        link = ET.Element("link")
        root.append(link)

        title = ET.SubElement(link, "title")
        link = ET.SubElement(link, "link")
        user = ET.SubElement(link, "user")
        scrapping_time = ET.SubElement(link, "scrapping_time")
        date = ET.SubElement(link, "date")

        title.text = url.title
        link.text = url.url
        user.text = url.user.username
        scrapping_time.text = str(url.scrapping_time)
        date.text = str(url.created_at)

    tree = minidom.parseString(ET.tostring(root)).toprettyxml(indent=" " * 4)
    save_path = Path(Config.FILES_DIR)
    if not save_path.exists():
        save_path.mkdir(parents=True, exist_ok=True)
    file_name = f"{uuid.uuid4()}.xml"
    with open(f"{save_path}/{file_name}", "w") as file:
        file.write(tree)
    return file_name


def create_fake_user() -> User:
    """This function generates SQLAlchemy User model instance with fake data

    Returns:
        User: SQLAlchemy User model instance
    """
    return User(
        username=fake.simple_profile()["username"],
        password=fake.password(length=12),
    )


def create_fake_site(user: User) -> Site:
    """This function generates SQLAlchemy User model instance with fake data

    Args:
        user (User): SQLAlchemy User model instance

    Returns:
        Site: SQLAlchemy Site model instance
    """
    return Site(
        user=user,
        url=fake.url(),
        title=" ".join(fake.words(nb=random.randint(1, 10))),
        scrapping_time=random.randint(0, 10000),
    )


def create_file_in_not_exists(func: Callable) -> Callable:
    """This decorator checks if LINKS_FILE exists or not empty
    if it is - creates a new file

    Args:
        func (Callable): function that creates LINKS_FILE

    Returns:
        Callable: decorated function
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if (
                not app.config["LINKS_FILE"].exists()
                or app.config["LINKS_FILE"].stat().st_size == 0
            ):
                func()
            res = f(*args, **kwargs)
            return res

        return wrapper

    return decorator
