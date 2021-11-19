import random
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path, PosixPath
from typing import List
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


def create_fake_user(instances: int = 1) -> List[User]:
    """Generate SQLAlchemy User model instance with fake data.

    Args:
        instances (int, optional): number of instances to create. Defaults to 1.

    Returns:
        Union[User, List[User]]: list of User model instances
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
        instances (int, optional): number of instances to create. Defaults to 1.

    Returns:
        Union[Site, List[Site]]: list of Site model instances
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
