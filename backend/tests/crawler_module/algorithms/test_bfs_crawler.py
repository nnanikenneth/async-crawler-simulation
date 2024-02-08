
import pytest
import asyncio
import aiohttp
import time
from pyppeteer import launch
from unittest.mock import MagicMock, patch
from backend.crawler_module.algorithms.bfs_crawler import BFSCrawler

@pytest.mark.asyncio
async def test_process_page_extracts_and_queues_links():
    crawler = BFSCrawler("https://example.com")
    page_url = "https://example.com/sample"
    # Mock page content
    page_content = '<a href="https://example.com/page1">Page 1</a><a href="https://example.com/page2">Page 2</a>'
    response_data = {'status': 'success', 'content': page_content}

    # Mock it to return a list of URLs
    mock_extract_links = MagicMock(return_value=["https://example.com/page1", "https://example.com/page2"])

    with patch.object(crawler.page_parser, 'extract_links_within_domain', new=mock_extract_links):
        await crawler.process_page(response_data, page_url)

        # Verify that the mocked extract_links_within_domain method was called with the page content
        mock_extract_links.assert_called_once_with(response_data, page_url)

        # Ensure the extracted URLs are added to the queue
        # Depending on your implementation, you might need to adjust how you check the queue
        queued_urls = []
        while not crawler.queue.empty():
            queued_urls.append(await crawler.queue.get())

        assert "https://example.com/page1" in queued_urls
        assert "https://example.com/page2" in queued_urls

@pytest.mark.asyncio
async def test_add_url():
    crawler = BFSCrawler(base_url="https://example.com")
    crawler.visited_urls = set()
    
    url_to_add = "https://example.com/page1"
    await crawler.add_url(url_to_add)
    assert url_to_add in crawler.queue._queue

    # Test that a visited URL is not added again
    crawler.visited_urls.add(url_to_add)
    await crawler.add_url(url_to_add)
    assert crawler.queue._queue.count(url_to_add) == 1  # The URL should not be added again

@pytest.mark.asyncio
async def test_initialization():
    base_url = "https://example.com"
    task_id = "test_task"
    request_delay = 1
    max_concurrency = 5

    crawler = BFSCrawler(base_url, task_id, request_delay, max_concurrency)

    assert crawler.url == base_url
    assert crawler.task_id == task_id
    assert crawler.request_delay == request_delay
    assert isinstance(crawler.semaphore, asyncio.Semaphore)
    assert crawler.semaphore._value == max_concurrency

@pytest.mark.asyncio
async def test_crawl():
    with patch.object(BFSCrawler, 'crawl_page', return_value=None):
        crawler = BFSCrawler("https://example.com")
        await crawler.queue.put("https://example.com/page1")
        await crawler.crawl()
        # Verify that the queue is empty after crawling
        assert crawler.queue.empty()

@pytest.mark.asyncio
async def test_get_next_url():
    crawler = BFSCrawler("https://example.com")
    await crawler.queue.put("https://example.com/page1")
    next_url = await crawler.get_next_url()
    assert next_url == "https://example.com/page1"

    no_url = await crawler.get_next_url()
    assert no_url is None

@pytest.mark.asyncio
async def test_has_more_urls():
    crawler = BFSCrawler("https://example.com")
    assert not crawler.has_more_urls()
    
    await crawler.queue.put("https://example.com/page1")
    assert crawler.has_more_urls()

@pytest.mark.asyncio
async def test_redirect_handling():
    crawler = BFSCrawler("https://example.com")
    original_url = "https://example.com/redirect"
    redirected_url = "https://example.com/target"

    # Mock response to simulate a redirect
    mock_response = {'status': 'redirect', 'new_url': redirected_url}

    with patch.object(crawler.page_fetcher, 'fetch_page', return_value=mock_response):
        await crawler.crawl_page(original_url)
        # The redirected URL should be in the queue
        assert await crawler.queue.get() == redirected_url

@pytest.mark.asyncio
async def test_crawler_respects_semaphore_limit():
    max_concurrency = 2
    crawler = BFSCrawler("https://example.com", max_concurrency=max_concurrency)
    crawler.page_fetcher.fetch_page = MagicMock(return_value={'status': 'success', 'content': 'page content'})

    # Simulate adding multiple URLs
    for i in range(5):
        await crawler.add_url(f"https://example.com/page{i}")

    # Track the number of concurrent tasks
    concurrent_tasks = 0
    max_concurrent_tasks = 0

    async def mock_crawl_page(url):
        nonlocal concurrent_tasks, max_concurrent_tasks
        concurrent_tasks += 1
        max_concurrent_tasks = max(max_concurrent_tasks, concurrent_tasks)
        await asyncio.sleep(0.01)  # Simulate work
        concurrent_tasks -= 1

    crawler.crawl_page = mock_crawl_page

    await crawler.crawl()

    assert max_concurrent_tasks <= max_concurrency
