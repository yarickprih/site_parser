import asyncio
import ssl
import time
from datetime import datetime
from typing import Awaitable, Callable, List, NoReturn, Tuple, Union

import aiohttp
import certifi
import requests
from bs4 import BeautifulSoup
from flask import current_app as app

from .models import Site, User


class RequestConfig:
    """Config variables for making HTTP requests."""

    WEBSITES_LIST_URL = "https://blog.feedspot.com/world_news_blogs/"
    HEADERS = {
        "cache-control": "max-age=0",
        "user-agent": "Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,\
            image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def parse_links() -> NoReturn:
    """Parse links from WEBSITES_LIST_URL and writes in to the file.

    Returns:
        NoReturn: NoReturn
    """
    selector = "a.ext"
    response = requests.get(
        RequestConfig.WEBSITES_LIST_URL, headers=RequestConfig.HEADERS
    )
    soup = BeautifulSoup(response.content, "lxml")
    links = [f"{link['href'].strip()}\n" for link in soup.select(selector=selector)]
    with open(app.config["LINKS_FILE"], "a") as file:
        for link in links:
            file.write(link)


async def fetch(
    session: aiohttp.ClientSession, url: str
) -> Tuple[str, Callable[[int], Awaitable[str]], time.time]:
    """Make an asynchronous request on given URL.

    Args:
        session (aiohttp.ClientSession): aiohttp Session
        url (str): URL to make request on

    Returns:
        Tuple[str, Callable[[int], Awaitable[str]], time.time]:
            url (str): URL that's had been requested
            result (Callable[[int], Awaitable[str]]): coroutine consisting response data
            time_ (time.time): Time in took to make a request
    """
    start = time.time()
    async with session.get(
        url, headers=RequestConfig.HEADERS, ssl_context=RequestConfig.SSL_CONTEXT
    ) as response:
        result = await response.read()
        end = time.time()
        time_ = end - start
        return url, result, time_


async def crawl(
    file_path: str,
) -> List[Callable[[int], Awaitable[str]]]:
    """Fetch links from text file with fetch()
    function and returns a list of asyncio coroutines.

    Returns:
        List[Callable[[int], Awaitable[str]]]: List of coroutines
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        with open(file_path, "r") as file:
            for url in file.readlines():
                task = fetch(session, url)
                tasks.append(task)
        tasks = await asyncio.gather(*tasks)
        return tasks


def create_site(
    user: User, url: str, data: str, time_: time.time
) -> dict[str, Union[str, User, int, datetime]]:
    """Create a URL instance with passed arguments.

    Args:
        user (User): SQLAlchemy User model instance
        url (str): URL string
        data (str): URL page body
        time_ (time.time): Time in took to make a request

    Returns:
        dict[str, Union[str, User, int, datetime]]: dictionary with Site
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


def create_site_list(user: User, file_path: str) -> List[Site]:
    """Create a list of SQLAlchemy Site model instances.

    Args:
        user (User): SQLAlchemy User model instance

    Returns:
        List[Site]: List of SQLAlchemy Site model instances
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(crawl(file_path))
    loop.close()
    for url, item, time_ in data:
        yield create_site(user, url, item, time_)
