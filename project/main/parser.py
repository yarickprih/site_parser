import asyncio
import json
import time
import typing as t
from pathlib import PosixPath

import aiohttp
import backoff
import requests
from bs4 import BeautifulSoup
from flask import current_app as app
from flask import flash
from project import db

from .models import Site, User
from .utils import create_site_dict


class RequestConfig:
    """Config variables for making HTTP requests."""

    WEBSITES_LIST_URL = "https://trends.netcraft.com/topsites"
    HEADERS = {
        "cache-control": "max-age=0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image\
            /avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;\
                v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) \
            AppleWebKit/605.1.15 (KHTML, like Gecko) \
                Version/13.1.1 Safari/605.1.15",
    }


def parse_links(
    url: t.Optional[str] = RequestConfig.WEBSITES_LIST_URL,
    selector: t.Optional[str] = "a",
    file_name: str = app.config["LINKS_FILE"],
) -> t.NoReturn:
    """Parse links from passed url by the css selector
    and write in into the file.

    Args:
        url (t.Optional[str], optional): URL to parse to links from.
            Defaults to RequestConfig.WEBSITES_LIST_URL.
        selector (t.Optional[str], optional): CSS selector of links to parse.
            Defaults to "a".
        file_name (str, optional): File name to save parsed links.
            Defaults to app.config["LINKS_FILE"].

    Returns:
        NoReturn
    """
    response = requests.get(
        url,
        headers=RequestConfig.HEADERS,
    )
    soup = BeautifulSoup(response.content, "lxml")
    links = [
        f"{link['href'].strip()}\n"
        for link in set(soup.select(selector=selector))
    ]
    with open(app.config["UPLOADS"] / file_name, "a") as file:
        for link in links:
            file.write(link)


@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    max_time=30,
)
@backoff.on_exception(
    backoff.expo,
    asyncio.TimeoutError,
    max_tries=3,
    max_time=50,
)
async def fetch(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    url: str,
) -> t.Tuple[str, t.Coroutine[t.Any, t.Any, bytes], float]:
    """Make an asynchronous request on given URL.

    Args:
        session (aiohttp.ClientSession): aiohttp Session
        semaphore (asyncio.Semaphore): asyncio loop Semaphore instance
        url (str): URL to make request on

    Returns:
        Tuple[str, Coroutine[Any, Any, bytes], time.time]:
            url (str): URL that's had been requested
            result Coroutine[Any, Any, bytes]): coroutine containing
            response data
            time_ (float): Time in took to make a request
    """
    async with semaphore:
        try:
            start = time.perf_counter()
            async with session.get(
                url,
                headers=RequestConfig.HEADERS,
                raise_for_status=True,
                timeout=30,
            ) as response:
                end = time.perf_counter()
                time_ = end - start
                result = await response.read()
                return url, result, time_
        except (
            aiohttp.ServerDisconnectedError,
            asyncio.TimeoutError,
        ) as e:
            app.logger.error(
                {
                    "url": url,
                    "error": e.__class__.__name__,
                    "message": e,
                }
            )
        except aiohttp.ClientConnectorError as e:
            app.logger.error(
                json.dumps(
                    {
                        "url": url,
                        "error": e.__class__.__name__,
                        "host": e.host,
                        "port": e.port,
                        "message": e.strerror,
                    },
                    indent=4,
                )
            )
        except aiohttp.ClientResponseError as e:
            app.logger.error(
                json.dumps(
                    {
                        "url": url,
                        "error": e.__class__.__name__,
                        "status_code": e.status,
                        "message": e.message,
                    },
                    indent=4,
                )
            )
        except Exception as e:
            app.logger.error(
                {
                    "url": url,
                    "error": e.__class__.__name__,
                    "message": str(e),
                }
            )


async def crawl(
    file_path: str,
    semaphore: asyncio.Semaphore,
) -> t.List[t.Callable[[t.Any], t.Awaitable[t.Any]]]:
    """Fetch links from text file with fetch()
    function and returns a list of asyncio coroutines.

    Args:
        file_path (str): name of the file to crawl
        semaphore (asyncio.Semaphore): asyncio loop Semaphore instance

    Returns:
        List[Callable[[Any], Awaitable[str]]]: List of coroutines
    """
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        with open(file_path, "r") as file:
            links = set(url[:-1] for url in file.readlines())
            tasks = [fetch(session, semaphore, url) for url in links]
        return await asyncio.gather(*tasks)


def create_sites_list(
    user: User, file_path: str
) -> t.Iterator[t.Dict[str, t.Any]]:
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
    semaphore = asyncio.BoundedSemaphore(500)
    data = loop.run_until_complete(crawl(file_path, semaphore))
    exceptions_counter = 0
    for item in data:
        if not item:
            exceptions_counter += 1
            continue
        url, body, time_ = item
        yield create_site_dict(user, url, body, time_)
    if exceptions_counter:
        flash(
            f"{exceptions_counter} site{'s' if exceptions_counter > 2 else ''}\
                 ha{'ve' if exceptions_counter > 1 else 's'}n't \
                     been parsed due the connection errors!",
            category="warning",
        )


def commit_parsed(user: User, file_path: PosixPath) -> None:
    """Parse and commit sites to the database.
    It creates list of asynchronously parsed sites
    that are committed to the database.
    Args:
        user (User): User model instance
        file_path (PosixPath): path to the file to parse
    """
    sites = create_sites_list(user, file_path)
    for site in sites:
        app.logger.info(f"Working... {site['url']}")
        Site.update_or_create(site)
    db.session.commit()
