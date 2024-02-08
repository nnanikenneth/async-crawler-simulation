from bs4 import BeautifulSoup
import pytest
from unittest.mock import MagicMock, patch
from backend.crawler_module.algorithms.utils.page_parser import PageParser

@pytest.mark.parametrize("html_content,expected_links", [
    ("""
    <html>
        <body>
            <a href="/about">About Us</a>
            <a href="http://www.example.com/contact">Contact</a>
            <a href="https://external.com">External Site</a>
        </body>
    </html>
    """, ["http://www.example.com/about", "http://www.example.com/contact"])
])
def test_parse_html_page(html_content, expected_links):
    page_parser = PageParser()
    domain_base_url = "http://www.example.com"
    actual_links = page_parser.parse_html_page(html_content.encode('utf-8'), domain_base_url)
    assert set(actual_links) == set(expected_links), "Extracted links should match expected links within the same domain"


@pytest.mark.parametrize("url,expected", [
    ("http://www.example.com", True),
    ("https://www.example.com", True),
    ("ftp://www.example.com", False),
    ("www.example.com", False)
])
def test_is_valid_url(url, expected):
    page_parser = PageParser()
    assert page_parser.is_valid_url(url) == expected, f"URL {url} validity should be {expected}"


@pytest.mark.parametrize("content_type,expected", [
    ("text/html; charset=utf-8", True),
    ("application/json", False)
])
def test_content_type_is_html(content_type, expected):
    page_parser = PageParser()
    assert page_parser.content_type_is_html(content_type) == expected

@pytest.mark.parametrize("content_type,expected", [
    ("application/json", True),
    ("text/html; charset=utf-8", False)
])
def test_content_type_is_json(content_type, expected):
    page_parser = PageParser()
    assert page_parser.content_type_is_json(content_type) == expected
