import pytest
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from backend.crawler_module.algorithms.incremental_crawler import IncrementalCrawler
from unittest.mock import ANY


@pytest.mark.asyncio
async def test_initialization():
    revisit_interval = 3600  # seconds
    request_delay = 1  # second
    max_concurrency = 5
    crawler = IncrementalCrawler(
        "https://example.com",
        task_id="test_task",
        revisit_interval=revisit_interval,
        request_delay=request_delay,
        max_concurrency=max_concurrency
    )

    assert crawler.base_url == "https://example.com"
    assert crawler.task_id == "test_task"
    assert crawler.revisit_interval == timedelta(seconds=revisit_interval)
    assert crawler.request_delay == request_delay
    assert crawler.max_concurrency == max_concurrency
    assert isinstance(crawler.semaphore, asyncio.Semaphore)
    assert crawler.semaphore._value == max_concurrency


@pytest.mark.asyncio
async def test_add_url_within_revisit_interval():
    crawler = IncrementalCrawler(
        "https://example.com", revisit_interval=3600)  # 1 hour
    url = "https://example.com/page1"

    # Add URL for the first time
    await crawler.add_url(url)
    assert (url, ANY) in crawler.queue, "URL should be added on first addition"

    # Attempt to add the same URL within the revisit interval
    await crawler.add_url(url)
    # The queue should still only have one instance of the URL
    assert crawler.queue.count(
        (url, ANY)) == 1, "URL should not be re-added within the revisit interval"


@pytest.mark.asyncio
async def test_get_next_url():
    crawler = IncrementalCrawler("https://example.com", revisit_interval=3600)
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"

    await crawler.add_url(url1)
    await crawler.add_url(url2)

    # Retrieve the first URL
    retrieved_url = await crawler.get_next_url()
    assert retrieved_url == url1, "Should retrieve the first URL added to the queue"
    # Verify the queue now only contains the second URL
    assert len(
        crawler.queue) == 1 and crawler.queue[0][0] == url2, "Queue should only contain the second URL"


@pytest.mark.asyncio
async def test_has_more_urls():
    crawler = IncrementalCrawler("https://example.com", revisit_interval=3600)

    assert not crawler.has_more_urls(), "Should indicate no more URLs initially"

    await crawler.add_url("https://example.com/page1")
    assert crawler.has_more_urls(), "Should indicate there are more URLs after addition"
