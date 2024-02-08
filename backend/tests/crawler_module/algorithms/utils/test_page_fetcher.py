from backend.crawler_module.algorithms.utils.page_fetcher import PageFetcher
from aioresponses import aioresponses
from unittest.mock import patch
import pytest

@pytest.mark.asyncio
async def test_session_management():
    fetcher = PageFetcher()
    assert fetcher.session is None, "Session should initially be None"
    
    await fetcher.init_session()
    assert fetcher.session is not None, "Session should be initialized"
    
    await fetcher.close_session()
    assert fetcher.session.closed, "Session should be closed after close_session"

@pytest.mark.asyncio
async def test_fetch_page_success():
    url = "https://example.com"
    mock_content = b"<html></html>"
    
    with aioresponses() as m:
        m.get(url, status=200, body=mock_content, content_type='text/html')
        
        fetcher = PageFetcher()
        await fetcher.init_session()  # Ensure the session is initialized
        response = await fetcher.fetch_page(url)
        
        assert response['status'] == 'success', "Status should be 'success' for successful fetches"
        assert response['content'] == mock_content, "Content should match the mocked response"
        await fetcher.close_session()

@pytest.mark.asyncio
async def test_robots_txt_compliance():
    url = "https://example.com/disallowed"
    robots_txt_url = "https://example.com/robots.txt"
    robots_txt_content = """
    User-agent: *
    Disallow: /disallowed
    """
    
    with aioresponses() as m:
        m.get(robots_txt_url, status=200, body=robots_txt_content)
        m.get(url, status=200)
        
        fetcher = PageFetcher()
        await fetcher.init_session()
        response = await fetcher.fetch_page(url)
        
        assert response['status'] == 'disallowed', "Fetch should be disallowed by robots.txt rules"
        await fetcher.close_session()

@pytest.mark.asyncio
async def test_fetch_page_returns_content_successfully():
    url = "https://example.com/success"
    expected_content = b"<html>Test</html>"

    with aioresponses() as m:
        m.get(url, status=200, body=expected_content, headers={'Content-Type': 'text/html'})

        fetcher = PageFetcher()
        await fetcher.init_session()
        response = await fetcher.fetch_page(url)
        assert response['status'] == 'success', "Fetch should be successful"
        assert response['content'] == expected_content, "Fetched content should match expected content"
        await fetcher.close_session()

