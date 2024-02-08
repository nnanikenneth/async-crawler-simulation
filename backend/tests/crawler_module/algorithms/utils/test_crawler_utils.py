import pytest
import asyncio
import aiohttp
import time
from pyppeteer import launch
from unittest.mock import MagicMock, patch
from backend.crawler_module.algorithms.utils.crawler_utils import normalize_url, add_to_found_links, is_same_domain, extract_domain, write_to_file

def test_normalize_url():
    assert normalize_url("http://example.com/section/", "article1.html") == "http://example.com/section/article1.html"
    assert normalize_url("http://example.com/section/subsection/", "../article2.html") == "http://example.com/section/article2.html"
    assert normalize_url("http://example.com", "/about") == "http://example.com/about"

def test_extract_domain():
    assert extract_domain("http://example.com/page") == "example.com"
    assert extract_domain("https://www.example.com:8000/page") == "www.example.com:8000"
    assert extract_domain("ftp://example.com/resource") == "example.com"

def test_is_same_domain():
    assert is_same_domain("http://example.com/page1", "http://example.com/page2")
    assert not is_same_domain("http://example.com", "http://another.com")
    assert is_same_domain("https://www.example.com", "http://www.example.com")

def test_add_to_found_links():
    found_links = []
    add_to_found_links("http://example.com/page", found_links)
    assert "http://example.com/page" in found_links
    add_to_found_links("http://example.com/about", found_links)
    assert "http://example.com/about" in found_links
    assert len(found_links) == 2

def test_write_to_file(tmp_path):
    output_file = tmp_path / "crawler_log.txt"
    url = "http://example.com"
    links = ["http://example.com/page1", "http://example.com/page2"]
    
    write_to_file(url, links, str(output_file))
    
    with open(output_file, "r") as file:
        content = file.read()
    
    assert "Visited: http://example.com" in content
    for link in links:
        assert f"  - {link}" in content