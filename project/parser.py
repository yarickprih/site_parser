import asyncio
import random
import time
from typing import Awaitable, Callable, List, NoReturn, Tuple

import aiohttp
import requests
from bs4 import BeautifulSoup
from flask import current_app as app

from .models import Site, User
from .utils import create_file_in_not_exists

WEBSITES_LIST_URL = "https://www.sitebuilderreport.com/inspiration/blog-examples"
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36",
]
user_agent = random.choice(user_agents)
HEADERS = {
    "authority": "httpbin.org",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": user_agent,
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
}


def parse_links() -> NoReturn:
    """This function parses links from WEBSITES_LIST_URL and writes in to the file

    Returns:
        NoReturn: NoReturn
    """
    selector = "div.sticky-bar > div > h2 > a"
    response = requests.get(WEBSITES_LIST_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "lxml")
    with open(app.config["LINKS_FILE"], "a") as file:
        for link in soup.select(selector=selector):
            file.write(f"{link['href'].strip()}\n")


async def fetch(
    session: aiohttp.ClientSession, url: str
) -> Tuple[str, Callable[[int], Awaitable[str]], time.time]:
    """This function makes an asynchronous request on given URL

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
    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            pass
        result = await response.text()
        end = time.time()
        time_ = end - start
        return url, result, time_


async def crawl() -> List[Callable[[int], Awaitable[str]]]:
    """This function fetches links from text file with fetch() function
    and returns a list of asyncio coroutines

    Returns:
        List[Callable[[int], Awaitable[str]]]: List of coroutines
    """
    async with aiohttp.ClientSession(trust_env=True) as session:
        tasks = []
        with open(app.config["LINKS_FILE"], "r") as file:
            for url in file.readlines():
                tasks.append(fetch(session, url))
        tasks = await asyncio.gather(*tasks)
        return tasks


def create_site(user: User, url: str, data: str, time_: time.time) -> Site:
    """This function create a SQLAlchemy Site model instance with passed arguments

    Args:
        user (User): SQLAlchemy User model instance
        url (str): URL string
        data (str): URL page body
        time_ (time.time): Time in took to make a request

    Returns:
        Site: SQLAlchemy Site model instance
    """
    soup = BeautifulSoup(data, "lxml")
    return Site(
        user=user,
        url=url[:-1],
        title=soup.select_one("title").text.strip(),
        scrapping_time=int(time_ * 1000),
    )


@create_file_in_not_exists(parse_links)
def create_site_list(user: User) -> List[Site]:
    """This function creates a list of SQLAlchemy Site model instances

    Args:
        user (User): SQLAlchemy User model instance

    Returns:
        List[Site]: List of SQLAlchemy Site model instances
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(crawl())
    loop.close()
    sites = []
    for url, item, time_ in data:
        try:
            sites.append(create_site(user, url, item, time_))
        except Exception:
            continue
    return sites
