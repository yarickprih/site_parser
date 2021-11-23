import asyncio
import time
from datetime import datetime
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    List,
    NoReturn,
    Tuple,
)

import aiohttp
import requests
from bs4 import BeautifulSoup
from flask import current_app as app

from .models import Site, User


class RequestConfig:
    """Config variables for making HTTP requests."""

    WEBSITES_LIST_URL = "https://trends.netcraft.com/topsites"
    HEADERS = {
        "cache-control": "max-age=0",
        "user-agent": "Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,\
            image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    PROXY = "http://142.93.24.89:3128"


def parse_links() -> NoReturn:
    """Parse links from WEBSITES_LIST_URL and writes in to the file.

    Returns:
        NoReturn: NoReturn
    """
    selector = "div > table > tbody > tr > td:nth-child(2) > a"

    response = requests.get(
        RequestConfig.WEBSITES_LIST_URL,
        headers=RequestConfig.HEADERS,
    )
    soup = BeautifulSoup(response.content, "lxml")
    links = [f"{link['href'].strip()}\n" for link in soup.select(selector=selector)]
    with open(app.config["LINKS_FILE"], "a") as file:
        for link in links:
            file.write(link)


async def fetch(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    url: str,
) -> Tuple[str, Callable[[int], Awaitable[str]], time.time]:
    """Make an asynchronous request on given URL.

    Args:
        session (aiohttp.ClientSession): aiohttp Session
        semaphore (asyncio.Semaphore): asyncio loop Semaphore instance
        url (str): URL to make request on

    Returns:
        Tuple[str, Callable[[int], Awaitable[str]], time.time]:
            url (str): URL that's had been requested
            result (Callable[[int], Awaitable[str]]): coroutine consisting response data
            time_ (time.time): Time in took to make a request
    """
    async with semaphore:
        start = time.perf_counter()
        async with session.get(url, headers=RequestConfig.HEADERS) as response:
            end = time.perf_counter()
            time_ = end - start
            result = await response.read()
            return url, result, time_


async def crawl(
    file_path: str,
    semaphore: asyncio.Semaphore,
) -> List[Callable[[int], Awaitable[str]]]:
    """Fetch links from text file with fetch()
    function and returns a list of asyncio coroutines.

    Args:
        file_path (str): name of the file to crawl
        semaphore (asyncio.Semaphore): asyncio loop Semaphore instance

    Returns:
        List[Callable[[int], Awaitable[str]]]: List of coroutines
    """
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(verify_ssl=False),
        trust_env=True,
    ) as session:
        with open(file_path, "r") as file:
            tasks = [fetch(session, semaphore, url) for url in file.readlines()]
        tasks = await asyncio.gather(*tasks)
        return tasks


def create_site_dict(
    user: User, url: str, data: str, time_: time.time
) -> Dict[str, Any]:
    """Create a dictionary of Site model attributes and values
    with passed arguments.

    Args:
        user (User): SQLAlchemy User model instance
        url (str): URL string
        data (str): URL page body
        time_ (time.time): Time in took to make a request

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


def create_sites_list(user: User, file_path: str) -> Iterator[Dict[str, Any]]:
    """Create a list of SQLAlchemy Site model instances.

    Args:
        user (User): SQLAlchemy User model instance
        file_path (str): destination to user uploaded file with links to parse

    Returns:
        Dict[str, Any]: dictionary with Site
        model attributes and values

    Yields:
        Iterator[Dict[str, Any]]: generator that results dictionary with Site
        model attributes and values
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    semaphore = asyncio.Semaphore(500)
    data = loop.run_until_complete(crawl(file_path, semaphore))
    loop.close()
    for url, item, time_ in data:
        yield create_site_dict(user, url, item, time_)
