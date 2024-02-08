import asyncio
import json
from bs4 import BeautifulSoup
from .crawler_utils import is_same_domain, normalize_url
from .page_fetcher import PageFetcher

class PageParser:
    """
    A class to parse web page content and extract URLs that are both valid and belong to the same domain.
    Supports parsing of both HTML and JSON content.
    """

    def is_valid_and_same_domain(self, complete_url, domain_base_url):
        """
        Checks if the URL is valid and belongs to the same domain as the base URL.
        """
        return self.is_valid_url(complete_url) and is_same_domain(
            complete_url, domain_base_url
        )

    def extract_links_within_domain(self, response_data, domain_base_url):
        """
        Extracts links that are within the same domain from the given page content.
        """
        content = response_data.get("content")
        content_type = response_data.get("content_type")
        if content:
            if self.content_type_is_html(content_type):
                return self.parse_html_page(content, domain_base_url)
            elif self.content_type_is_json(content_type):
                return self.parse_json_page(content, domain_base_url)
        return []

    def parse_html_page(self, content, domain_base_url):
        """
        Parses HTML content to extract all links within the same domain.
        """
        html = content.decode("utf-8")  # Assuming content is bytes
        soup = BeautifulSoup(html, "html.parser")
        extracted_links = set()
        for anchor_tag in soup.find_all("a", href=True):
            complete_url = normalize_url(domain_base_url, anchor_tag["href"])
            if self.is_valid_and_same_domain(complete_url, domain_base_url):
                extracted_links.add(complete_url)
        return list(extracted_links)

    def parse_json_page(self, content, domain_base_url):
        """
        Parses JSON content to extract URLs. TODO: This method needs to be implemented based on your JSON structure.
        """
        data = json.loads(content.decode("utf-8"))
        extracted_links = set()
        return list(extracted_links)

    def is_valid_url(self, url):
        """
        Validates URLs to ensure they begin with 'http://' or 'https://'.
        TODO: Additional logic can be added here to validate URLs more thoroughly
        """
        return url.startswith("http://") or url.startswith("https://")

    def content_type_is_html(self, content_type):
        """
        Checks if the content type is HTML.
        """
        return "text/html" in content_type.lower()

    def content_type_is_json(self, content_type):
        """
        Checks if the content type is JSON.
        """
        return "application/json" in content_type.lower()


# Example usage
"""
async def main():
    page_fetcher = PageFetcher()
    page_parser = PageParser()
    await page_fetcher.init_session()

    url = "https://www.monzo.com"
    response_data = await page_fetcher.fetch_page(url)
    if response_data['status'] == 'success':
        found_links = page_parser.extract_links_within_domain(response_data, url)
        print(found_links)

    await page_fetcher.close_session()

if __name__ == "__main__":
    asyncio.run(main())
"""
