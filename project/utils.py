import random
import uuid
import xml.etree.ElementTree as ET
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Union
from xml.dom import minidom

from faker import Faker
from flask import current_app as app

from .config import Config
from .models import Site, User

fake = Faker()


def create_xml_report(urls: List[Site]) -> str:
    """Create an XML report file.

    Creates an XML report file with info on a list of Site database model instances

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
        url_str = ET.SubElement(link, "url")
        user = ET.SubElement(link, "user")
        scrapping_time = ET.SubElement(link, "scrapping_time")
        date = ET.SubElement(link, "date")

        title.text = url.title
        url_str.text = url.url
        user.text = url.user.username
        scrapping_time.text = str(url.scrapping_time)
        date.text = url.created_at.strftime("%B %d %Y")

    tree = minidom.parseString(ET.tostring(root)).toprettyxml(indent=" " * 4)
    save_path = Path(Config.FILES_DIR)
    if not save_path.exists():
        save_path.mkdir(parents=True, exist_ok=True)
    file_name = f"{uuid.uuid4()}.xml"
    with open(f"{save_path}/{file_name}", "w") as file:
        file.write(tree)
    return file_name


def create_fake_user(n: int = 1) -> Union[User, List[User]]:
    """Generate SQLAlchemy User model instance with fake data.

    Args:
        n (int, optional): number of instances to create. Defaults to 1.

    Returns:
        Union[User, List[User]]: SQLAlchemy User model instance or list of User model instances
    """
    user = User(
        username=fake.simple_profile()["username"],
        password=fake.password(length=12),
    )
    return [user for _ in range(n)] if n > 1 else user


def create_fake_site(user: User, n: int = 1) -> Union[Site, List[Site]]:
    """Generate SQLAlchemy User model instance with fake data.

    Args:
        user (User): SQLAlchemy User model instance
        n (int, optional): number of instances to create. Defaults to 1.

    Returns:
        Union[Site, List[Site]]: SQLAlchemy Site model instance or list of Site model instances
    """
    site = Site(
        user=user,
        url=fake.url(),
        title=" ".join(fake.words(nb=random.randint(1, 10))),
        scrapping_time=random.randint(0, 10000),
    )
    return [site for _ in range(n)] if n > 1 else site


def create_file_in_not_exists(func: Callable) -> Callable:
    """Check if LINKS_FILE exists or not empty.

    Decorator to check if LINKS_FILE exists or not empty to.
    If it is - calls the function that creates a new LINKS_FILE.

    Args:
        func (Callable): function that creates LINKS_FILE

    Returns:
        Callable: decorated function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            if (
                not app.config["LINKS_FILE"].exists()
                or app.config["LINKS_FILE"].stat().st_size == 0
            ):
                func()
            res = f(*args, **kwargs)
            return res

        return wrapper

    return decorator
