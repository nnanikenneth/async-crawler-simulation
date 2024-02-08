import aiohttp
import asyncio
import logging
import traceback
from .utils.page_fetcher import PageFetcher
from .utils.page_parser import PageParser
from .base_crawler import BaseCrawler
from ..configs.logger_config import LoggerConfig
from ..configs.crawler_config import CrawlerConfig
from .utils.crawler_utils import add_to_found_links

LoggerConfig.setup_logging()

class DFSCrawler(BaseCrawler):
    """
    The DFSCrawler class, inheriting from BaseCrawler, implements a depth-first search (DFS) algorithm to crawl websites asynchronously. It is designed to efficiently navigate through web pages within a given domain starting from a base URL, respecting a set delay between requests to avoid overwhelming the server.

    Key Features:
    - Initializes with a base URL, optional task ID for tracking, request delay to control crawl speed, and maximum concurrency to limit simultaneous requests.
    - Utilizes an asyncio semaphore to manage concurrency, ensuring no more than the specified number of concurrent requests.
    - Employs a stack to navigate through URLs in a depth-first manner, with a configurable maximum depth to limit the crawl scope.
    - Processes each page by fetching its content, parsing for links within the same domain, and recursively scheduling new crawl tasks for each discovered link.
    - Tracks visited URLs to prevent re-crawling and efficiently manages tasks to maintain active crawling up to the concurrency limit.

    Attributes:
    - stack: A list to manage URLs in LIFO order for DFS traversal.
    - max_depth: Maximum depth to crawl, limiting the scope of the search.
    - request_delay: Time delay between requests to prevent overwhelming the server.
    - page_fetcher: A PageFetcher instance for fetching web pages.
    - page_parser: A PageParser instance for extracting links from pages.
    - lock: An asyncio Lock to ensure thread-safe operations on shared data like the stack.
    - max_concurrency: Maximum number of concurrent requests to avoid server overload.
    - task_id: An optional identifier for the crawling task.
    - semaphore: An asyncio Semaphore to control the concurrency level of the crawler.

    Usage:
    Ideal for developers implementing custom web crawlers for SEO analysis, data collection, or website monitoring, offering a scalable and customizable foundation. Modify request_delay and max_concurrency to suit target website's tolerance and desired crawl rate.

    Note: This class requires Python's asyncio for asynchronous operations and aiohttp for HTTP requests. Ensure proper handling of redirects and error responses for comprehensive coverage.
    """
    def __init__(self, base_url, task_id=None, request_delay=0, max_concurrency=5):
        super().__init__(base_url)
        self.stack = []
        self.max_depth = CrawlerConfig.DFS_ALGORITHM_MAX_DEPTH
        self.request_delay = request_delay
        self.page_fetcher = PageFetcher() 
        self.page_parser = PageParser()
        self.lock = asyncio.Lock() 
        self.max_concurrency = max_concurrency
        self.task_id = task_id
        self.semaphore = asyncio.Semaphore(max_concurrency)  

    async def add_url(self, url, depth):
        """
        Adds a URL to the stack if it has not been visited and is within the maximum depth.
        """
        async with self.lock:
            if url not in self.visited_urls and depth <= self.max_depth:
                self.stack.append((url, depth))

    async def get_next_url(self):
        """
        Pops the next URL from the stack to visit, following the LIFO order of DFS.
        """
        async with self.lock:
            if self.stack:
                return self.stack.pop()
        return None, None

    async def crawl(self):
        """
        Main crawling function that manages the crawling process, including fetching and parsing pages.
        """
        await self.page_fetcher.init_session()
        tasks = []
        await self.add_url(self.base_url, 0)
        while self.stack or tasks:
            # Ensure we do not launch more tasks than the semaphore limit
            if self.stack and len(tasks) < self.semaphore._value:
                url, depth = await self.get_next_url()
                if url and url not in self.visited_urls:
                    self.visited_urls.add(url)
                    def make_callback(url):
                        def callback(task):
                            self.task_completed_callback(task, url)
                        return callback
                    task = asyncio.create_task(self.crawl_page(url, depth))
                    task.add_done_callback(make_callback(url))
                    tasks.append(task)
            else:
                completed, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = list(pending)
        await self.page_fetcher.close_session()

    def task_completed_callback(self, task, url):
        """
        Callback function for handling completed crawl tasks, including logging errors.
        """
        try:
            task.result()
        except Exception as e:
            logging.error(f"Exception caught while processing URL {url}: {e}")

    async def crawl_page(self, url, depth):
        """
        Fetches and processes a single web page, scheduling new URLs found for crawling.
        """
        async with self.semaphore:
            try:
                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)
                response_data = await self.page_fetcher.fetch_page(url)  
                if response_data['status'] == 'success':
                    await self.process_page(response_data, url, depth)
                elif response_data['status'].startswith('redirect') and response_data['new_url']:
                    # Optionally handle redirects here, if you wish to follow them
                    await self.add_url(response_data['new_url'], depth)
            except aiohttp.ClientError as e:
                self.handle_error(e, url)

    async def process_page(self, response_data, url, depth):
        """
        Processes the content of a fetched page, extracting and scheduling new URLs to crawl.
        """
        logging.info(f"Visiting URL with task_id {self.task_id}: {url}")
        found_links = []

        if response_data['content']:
            full_urls = self.page_parser.extract_links_within_domain(response_data, url)
            for full_url in full_urls:
                if full_url not in self.visited_urls:  
                    await self.add_url(full_url, depth)
                    add_to_found_links(full_url, found_links)

        self.map_url_to_found_links(url, found_links)
        logging.info(f"Links found on {url} with task_id {self.task_id}: {found_links}")
    
    def has_more_urls(self):
        """
        Checks if there are more URLs to crawl.
        """
        return bool(self.stack)

# Example usage
base_url = 'https://monzo.com'  
task_id = 'example_task_001'  # Optional task ID for tracking
max_concurrency = 5 
crawler = DFSCrawler(base_url, task_id=task_id, max_concurrency=max_concurrency) 

async def main():
    await crawler.crawl()  # Start crawling process

if __name__ == "__main__":
    asyncio.run(main()) 

