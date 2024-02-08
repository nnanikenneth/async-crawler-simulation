import pytest
from aioresponses import aioresponses
import aiohttp
import pytest
from backend.crawler_module.crawler_middlewares.robotstxt import RobotsTxt


@pytest.mark.asyncio
async def test_missing_robots_txt():
    with aioresponses() as m:
        m.get('https://example.com/robots.txt', status=404)

        async with aiohttp.ClientSession() as session:
            robots_txt = RobotsTxt(session)
            is_allowed = await robots_txt.is_fetch_allowed("AnyUserAgent", "https://example.com/anywhere")
            assert is_allowed, "Fetching should be allowed if robots.txt is missing"


@pytest.mark.asyncio
async def test_fetch_and_parse_robots_txt():
    robots_txt_content = """
    User-agent: *
    Disallow: /disallowed
    """

    base_url = "https://example.com"
    robots_txt_url = f"{base_url}/robots.txt"

    with aioresponses() as m:
        m.get(robots_txt_url, status=200, body=robots_txt_content)

        async with aiohttp.ClientSession() as session:
            robots_txt = RobotsTxt(session)
            parser = await robots_txt.get_or_create_parser(base_url)
            assert parser is not None, "A parser should be created for domains with robots.txt"
            assert base_url in robots_txt.parsers, "Domain should be cached after fetching robots.txt"


@pytest.mark.asyncio
async def test_fetching_allowed_by_robots_txt():
    robots_txt_content = """
    User-agent: ExampleCrawler
    Disallow: /disallowed
    """
    base_url = "https://example.com"
    allowed_url = f"{base_url}/allowed"
    disallowed_url = f"{base_url}/disallowed"

    with aioresponses() as m:
        m.get(f"{base_url}/robots.txt", status=200, body=robots_txt_content)

        async with aiohttp.ClientSession() as session:
            robots_txt = RobotsTxt(session)
            is_allowed = await robots_txt.is_fetch_allowed("ExampleCrawler", allowed_url)
            assert is_allowed, "Fetching should be allowed for URLs not disallowed by robots.txt"

            is_disallowed = await robots_txt.is_fetch_allowed("ExampleCrawler", disallowed_url)
            assert not is_disallowed, "Fetching should be disallowed for URLs explicitly disallowed by robots.txt"
