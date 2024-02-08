import aiohttp
import asyncio
import logging

from .utils.page_fetcher import PageFetcher
from .utils.page_parser import PageParser
from .base_crawler import BaseCrawler
from ..configs.logger_config import LoggerConfig
from .utils.crawler_utils import add_to_found_links

LoggerConfig.setup_logging()

class BFSCrawler(BaseCrawler):
    """
    The BFSCrawler class extends the BaseCrawler to implement a Breadth-First Search (BFS) approach for web crawling.
    This crawler methodically visits and inspects all the pages of a website by following links from the base URL outwards, level by level.

    Attributes:
        queue: An asyncio Queue that holds URLs to be crawled in FIFO order.
        url: The base URL to start crawling from.
        request_delay: Optional delay between requests to avoid overloading the server.
        page_fetcher: Component to fetch the content of a page.
        page_parser: Component to parse the content of a page and extract links.
        session: An aiohttp.ClientSession for making HTTP requests. Initialized later in an async context.
        task_id: An optional identifier for the crawl task.
        max_retries: The maximum number of retries for a request before giving up.
        semaphore: A semaphore to limit the number of concurrent requests and avoid overwhelming the server.
    """
    def __init__(self, base_url, task_id=None, request_delay=0, max_concurrency=10):
        super().__init__(base_url)
        self.queue = asyncio.Queue() # Initializes the queue for managing URLs
        self.url = base_url  # Stores the base URL
        self.request_delay = request_delay # Sets the request delay
        self.page_fetcher = PageFetcher()  # Instantiates the page fetcher
        self.page_parser = PageParser()    # Instantiates the page parser
        self.task_id = task_id # Sets the task ID
        self.max_retries = 2
        self.semaphore = asyncio.Semaphore(max_concurrency)  # Semaphore to limit concurrent requests

    async def add_url(self, url):
        """
        Adds a new URL to the queue if it hasn't been visited yet.
        """
        if url not in self.visited_urls:
            await self.queue.put(url)

    async def get_next_url(self):
        """
        Retrieves the next URL from the queue if available.
        """
        if not self.queue.empty():
            return await self.queue.get()
        return None
    
    async def crawl(self):
        """
        The main crawling loop that manages the dispatching of crawl tasks.
        """
        await self.page_fetcher.init_session()
        await self.add_url(self.base_url)
        tasks = set()
        while not self.queue.empty() or tasks:
            while not self.queue.empty() and len(tasks) < self.semaphore._value:  # Check semaphore limit
                url = await self.get_next_url()
                if url not in self.visited_urls:
                    self.visited_urls.add(url)
                    def make_callback(url):
                        def callback(task):
                            self.task_completed_callback(task, url)
                        return callback
                    task = asyncio.create_task(self.crawl_page(url))
                    task.add_done_callback(make_callback(url))
                    tasks.add(task)
                    # Wait for at least one task to complete before launching more
                    if len(tasks) >= self.semaphore._value:
                        break 
            if tasks:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = pending
                
                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)  # Non-blocking sleep

        if tasks:
            await asyncio.gather(*tasks)
        await self.page_fetcher.close_session()  # Close the session after all tasks are done

    def task_completed_callback(self, task, url):
        """
        Callback function that is called upon task completion. It logs any exceptions encountered.
        """
        try:
            task.result()
        except Exception as e:
            logging.error(f"Exception caught while processing URL {url}: {e}")
    
    async def crawl_page(self, url):
        async with self.semaphore:  
            try:
                response_data = await self.page_fetcher.fetch_page(url) 
                if response_data['status'] == 'success' and response_data['content']:
                    await self.process_page(response_data, url)
                elif response_data['status'].startswith('redirect') and response_data['new_url']:
                    await self.add_url(response_data['new_url'])
            except aiohttp.ClientError as e:
                self.handle_error(e, url)

    async def process_page(self, response_data, url):
        """
        Processes the content of a fetched page, extracting and queuing new URLs to crawl.
        """
        # logging.info(f"Visiting URL with task_id {self.task_id} : {url}")
        found_links = []
        if response_data['content']:
            # Pass the entire response_data to the parser
            full_urls = self.page_parser.extract_links_within_domain(response_data, url)
            for full_url in full_urls:
                if full_url not in self.visited_urls:
                    await self.add_url(full_url)
                    add_to_found_links(full_url, found_links)

        self.map_url_to_found_links(url, found_links)
        # logging.info(f"Links found on {url} with task_id {self.task_id}: {found_links}")

    def has_more_urls(self):
        """
        Checks if there are more URLs in the queue to be crawled.
        """
        return not self.queue.empty()
    

# Example usage
"""
task_id = 'example_task_001'  # Optional task ID for tracking
crawler = BFSCrawler(base_url="https://monzo.com", task_id=task_id, request_delay=0)

async def main():
    await crawler.crawl()

if __name__ == "__main__":
    asyncio.run(main())
"""
