
import pytest
import asyncio
import aiohttp
import time
from pyppeteer import launch
from unittest.mock import MagicMock, patch
from backend.crawler_module.algorithms.dfs_crawler import DFSCrawler


@pytest.mark.asyncio
async def test_dfs_initialization():
    base_url = "https://example.com"
    task_id = "test_task"
    request_delay = 1
    max_concurrency = 5
    max_depth = 3

    crawler = DFSCrawler(base_url, task_id=task_id,
                         request_delay=request_delay, max_concurrency=max_concurrency)
    crawler.max_depth = max_depth

    assert crawler.base_url == base_url
    assert crawler.task_id == task_id
    assert crawler.request_delay == request_delay
    assert crawler.max_concurrency == max_concurrency
    assert crawler.max_depth == max_depth


@pytest.mark.asyncio
async def test_add_url_within_depth():
    crawler = DFSCrawler("https://example.com", max_concurrency=5)
    crawler.max_depth = 2

    await crawler.add_url("https://example.com/page1", 1)
    await crawler.add_url("https://example.com/page2", 2)
    await crawler.add_url("https://example.com/page3", 3)

    assert ("https://example.com/page1", 1) in crawler.stack
    assert ("https://example.com/page2", 2) in crawler.stack
    assert ("https://example.com/page3", 3) not in crawler.stack


@pytest.mark.asyncio
async def test_dfs_crawler_respects_max_concurrency():
    max_concurrency = 2
    crawler = DFSCrawler("https://example.com",
                         max_concurrency=max_concurrency)
    crawler.max_depth = 3

    # Mock response data to simulate found links on each page
    mock_response_data = {'status': 'success',
                          'content': '<a href="https://example.com/page1">Page 1</a>'}

    # Setup the mock for page_fetcher.fetch_page to control the flow
    async def mock_fetch_page(url):
        await asyncio.sleep(0.1)  # Simulate network delay
        return mock_response_data

    crawler.page_fetcher.fetch_page = mock_fetch_page

    # Counter to track the maximum number of concurrent tasks
    current_concurrency = 0
    max_concurrency_observed = 0

    # Override the crawl_page method to track concurrency
    original_crawl_page = crawler.crawl_page

    async def mock_crawl_page(url, depth):
        nonlocal current_concurrency, max_concurrency_observed
        current_concurrency += 1
        max_concurrency_observed = max(
            max_concurrency_observed, current_concurrency)
        try:
            # Call the original method to ensure we're testing the real functionality
            await original_crawl_page(url, depth)
        finally:
            current_concurrency -= 1

    crawler.crawl_page = mock_crawl_page

    await crawler.add_url("https://example.com/page1", 1)
    await crawler.add_url("https://example.com/page2", 1)

    await crawler.crawl()

    # Verify that the crawler never exceeded the max_concurrency limit
    assert max_concurrency_observed <= max_concurrency, \
        f"Max concurrency exceeded: {max_concurrency_observed} > {max_concurrency}"


@pytest.mark.asyncio
async def test_depth_tracking_across_pages():
    crawler = DFSCrawler("https://example.com", max_concurrency=2)
    crawler.max_depth = 2

    # Mock responses to simulate page content with links
    async def mock_fetch_page(url):
        if url == "https://example.com":
            return {'status': 'success', 'content': '<a href="https://example.com/page1">Page 1</a>'}
        elif url == "https://example.com/page1":
            return {'status': 'success', 'content': '<a href="https://example.com/page2">Page 2</a>'}
        return {'status': 'success', 'content': ''}

    crawler.page_fetcher.fetch_page = mock_fetch_page

    # Start the crawl and let it run through the mock pages
    await crawler.crawl()

    # Verify that page2 (depth 3) was not added due to depth limit
    assert ("https://example.com/page2",
            3) not in crawler.stack, "URLs beyond max depth should not be added"


@pytest.mark.asyncio
async def test_redirect_handling_maintains_depth():
    crawler = DFSCrawler("https://example.com", max_concurrency=5)
    redirect_url = "https://example.com/redirect"
    redirected_to_url = "https://example.com/target"
    depth = 1  # Initial depth for the redirected URL

    # Simulate the fetching process to immediately return a redirect response
    async def mock_fetch_page(url):
        if url == redirect_url:
            return {'status': 'redirect', 'new_url': redirected_to_url}
        return {'status': 'success', 'content': ''}

    crawler.page_fetcher.fetch_page = mock_fetch_page

    # Simulate crawling the redirect URL at a specific depth
    await crawler.crawl_page(redirect_url, depth)

    # Check that the redirected URL is added with the correct depth
    assert crawler.stack[-1] == (redirected_to_url,
                                 depth), "Redirected URL should be added to the stack maintaining the original depth"


@pytest.mark.asyncio
async def test_add_url():
    crawler = DFSCrawler("https://example.com", max_concurrency=5)
    await crawler.add_url("https://example.com/page1", 1)  # Adding at depth 1

    # Verify the URL is added with correct depth
    assert crawler.stack == [("https://example.com/page1", 1)
                             ], "URL should be added to the stack with correct depth"


@pytest.mark.asyncio
async def test_get_next_url():
    crawler = DFSCrawler("https://example.com", max_concurrency=5)
    await crawler.add_url("https://example.com/page1", 1)
    # This should be the next URL to crawl
    await crawler.add_url("https://example.com/page2", 2)

    url, depth = await crawler.get_next_url()

    # Verify the most recently added URL is returned first
    assert url == "https://example.com/page2" and depth == 2, "Should return the most recently added URL and its depth"


@pytest.mark.asyncio
async def test_has_more_urls():
    crawler = DFSCrawler("https://example.com", max_concurrency=5)
    assert not crawler.has_more_urls(), "Should report no URLs to crawl initially"

    await crawler.add_url("https://example.com/page1", 1)
    assert crawler.has_more_urls(), "Should report URLs to crawl after addition"
