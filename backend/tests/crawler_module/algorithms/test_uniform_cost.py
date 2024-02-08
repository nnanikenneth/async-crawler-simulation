import pytest
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from backend.crawler_module.algorithms.uniform_cost_crawler import UniformCostCrawler


@pytest.mark.asyncio
async def test_uniform_cost_crawler_initialization():
    crawler = UniformCostCrawler(
        "https://example.com", task_id="test_id", request_delay=1, max_concurrency=3)
    assert crawler.base_url == "https://example.com"
    assert crawler.task_id == "test_id"
    assert crawler.request_delay == 1
    assert crawler.max_concurrency == 3
    assert isinstance(crawler.semaphore, asyncio.Semaphore)
    assert crawler.semaphore._value == 3


@pytest.mark.asyncio
async def test_has_more_urls():
    crawler = UniformCostCrawler("https://example.com")
    assert not crawler.has_more_urls()
    await crawler.add_url("https://example.com/page1", cost=1)
    assert crawler.has_more_urls()


@pytest.mark.asyncio
async def test_add_url_with_cost():
    crawler = UniformCostCrawler("https://example.com")
    await crawler.add_url("https://example.com/page1", cost=2)
    assert crawler.priority_queue[0].url == "https://example.com/page1"
    assert crawler.priority_queue[0].cost == 2


@pytest.mark.asyncio
async def test_get_next_url():
    crawler = UniformCostCrawler("https://example.com")
    await crawler.add_url("https://example.com/page2", cost=2)
    # This should be retrieved first
    await crawler.add_url("https://example.com/page1", cost=1)

    next_url = await crawler.get_next_url()
    assert next_url == "https://example.com/page1"


@pytest.mark.asyncio
async def test_process_page_extracts_links():
    crawler = UniformCostCrawler("https://example.com")
    page_content = '<a href="https://example.com/page1">Page 1</a>'
    response_data = {'status': 'success', 'content': page_content}

    crawler.page_parser.extract_links_within_domain = MagicMock(
        return_value=["https://example.com/page1"])

    await crawler.process_page(response_data, "https://example.com")

    assert any(url_with_cost.url ==
               "https://example.com/page1" for url_with_cost in crawler.priority_queue), "URL should be extracted and added to the queue"


@pytest.mark.asyncio
async def test_crawl():
    crawler = UniformCostCrawler("https://example.com", max_concurrency=2)
    crawler.page_fetcher.fetch_page = MagicMock(
        return_value={'status': 'success', 'content': '<html></html>'})

    await crawler.add_url("https://example.com", cost=0)
    with patch('asyncio.sleep', return_value=None):
        await crawler.crawl()

    assert "https://example.com" in crawler.visited_urls
