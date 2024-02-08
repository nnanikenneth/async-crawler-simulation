import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from .utils.page_fetcher import PageFetcher
from .utils.page_parser import PageParser
from .base_crawler import BaseCrawler
from ..configs.logger_config import LoggerConfig
from .utils.crawler_utils import add_to_found_links

LoggerConfig.setup_logging()

class IncrementalCrawler(BaseCrawler):
    """
    The IncrementalCrawler class, inheriting from BaseCrawler, implements an incremental crawling strategy.
    It is designed to periodically revisit and crawl websites to update information or detect changes.

    Key Features:
    - Supports scheduling URLs for revisiting at specified intervals, allowing for regular updates without manual intervention.
    - Utilizes asyncio for asynchronous operations, enhancing efficiency and scalability.
    - Employs a queue system for managing URLs to visit and revisit, incorporating a timestamp to track when each URL was last crawled.
    - Limits the number of concurrent requests with an asyncio semaphore to prevent server overload and comply with rate limits.
    - Configurable request delay to further control crawl rate and respect server responsiveness.

    Usage:
    Ideal for applications requiring up-to-date data from specific web resources, such as content aggregators, search engines, or monitoring tools.
    Customize revisit intervals, request delay, and concurrency settings to balance timeliness, thoroughness, and server load.
    """
    def __init__(self, base_url, task_id=None, revisit_interval=None, request_delay=0, max_concurrency=5):
        super().__init__(base_url)
        self.queue = []
        self.revisit_interval = timedelta(seconds=revisit_interval) if revisit_interval else None
        self.request_delay = request_delay
        self.last_visited = {}
        self.page_fetcher = PageFetcher()
        self.page_parser = PageParser()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.task_id = task_id
        self.semaphore = asyncio.Semaphore(max_concurrency)  # Limit concurrent requests

    async def add_url(self, url):
        """
        Adds a URL to the queue for crawling if it meets revisit criteria or has not been visited.
        """
        async with self.lock:
            current_time = datetime.now()
            last_visited_time = self.last_visited.get(url, datetime.min)
            if self.revisit_interval is None or (current_time - last_visited_time) > self.revisit_interval:
                self.queue.append((url, current_time))
                self.last_visited[url] = current_time

    async def get_next_url(self):
        """
        Retrieves and removes the next URL from the queue to crawl, based on queue order.
        """
        async with self.lock:
            if self.queue:
                url, _ = self.queue.pop(0)
                return url
        return None

    async def crawl(self):
        """
        Main crawling function that manages the crawling process, including fetching and parsing pages.
        """
        await self.page_fetcher.init_session()
        self.queue.append((self.base_url, datetime.min))
        tasks = []
        while self.queue or tasks:
            if self.queue and len(tasks) < self.semaphore._value:
                url = await self.get_next_url()
                if url and url not in self.visited_urls:
                    self.visited_urls.add(url)
                    def make_callback(url):
                        def callback(task):
                            self.task_completed_callback(task, url)
                        return callback
                    task = asyncio.create_task(self.crawl_page(url))
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

    async def crawl_page(self, url):
        """
        Fetches and processes a single page, including handling redirects and extracting links.
        """
        async with self.semaphore:
            try:
                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)
                response_data = await self.page_fetcher.fetch_page(url) 
                if response_data['status'] == 'success' and response_data['content']:
                    await self.process_page(response_data, url)
                elif response_data['status'].startswith('redirect') and response_data['new_url']:
                    await self.add_url(response_data['new_url'])
            except aiohttp.ClientError as e:
                self.handle_error(e, url)

    async def process_page(self, response_data, url):
        """
        Processes page content, extracting links within the same domain and adding them to the queue.
        """
        # logging.info(f"Visiting URL with task_id {self.task_id} : {url}")
        found_links = []
        if response_data['content']:
            full_urls = self.page_parser.extract_links_within_domain(response_data, url)
            for full_url in full_urls:
                if full_url not in self.visited_urls:
                    await self.add_url(full_url)
                    add_to_found_links(full_url, found_links)

        self.map_url_to_found_links(url, found_links)
        # logging.info(f"Links found on {url} with task_id {self.task_id}: {found_links}")

    def has_more_urls(self):
        """
        Checks if there are more URLs to crawl.
        """
        return bool(self.queue)


# Example usage
"""
crawler = IncrementalCrawler("https://monzo.com", revisit_interval=3600, request_delay=0)

async def main():
    await crawler.crawl()

if __name__ == "__main__":
    asyncio.run(main())
"""
