import aiohttp
import asyncio
import heapq
import logging
from .utils.page_fetcher import PageFetcher
from .utils.page_parser import PageParser
from .base_crawler import BaseCrawler
from ..configs.logger_config import LoggerConfig
from .utils.crawler_utils import add_to_found_links

LoggerConfig.setup_logging()

class URLWithCost:
    """
    A helper class to encapsulate URLs with their associated crawling cost. 
    This allows URLs to be managed in a priority queue based on cost, facilitating 
    the uniform cost search strategy where lower cost URLs are prioritized.
    """
    def __init__(self, url, cost):
        self.url = url  # The URL to crawl
        self.cost = cost  # Cost associated with the URL

    def __lt__(self, other):
        # Comparison method for priority queue to sort URLs by their cost
        return self.cost < other.cost

class UniformCostCrawler(BaseCrawler):
    """
    The UniformCostCrawler extends BaseCrawler to implement uniform cost search for web crawling.
    It prioritizes crawling based on the cost associated with each URL, allowing for more strategic crawling of web resources.

    Features:
    - Uses a priority queue to manage crawl order based on URL costs.
    - Supports configurable request delay and concurrency limits to respect server load and avoid rate-limiting.
    - Utilizes asynchronous requests for efficient network utilization.
    """
    def __init__(self, base_url, task_id=None, request_delay=0, max_concurrency=5):
        super().__init__(base_url)
        self.priority_queue = []
        self.request_delay = request_delay
        self.page_fetcher = PageFetcher()  # Ensure PageFetcher's fetch_page method is async
        self.page_parser = PageParser()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.task_id = task_id
        self.semaphore = asyncio.Semaphore(max_concurrency)  # Control concurrency

    async def add_url(self, url, cost=1):
        """
        Adds a URL with an associated cost to the priority queue if it hasn't been visited.
        """
        async with self.lock:
            if url not in self.visited_urls:
                heapq.heappush(self.priority_queue, URLWithCost(url, cost))

    async def get_next_url(self):
        """
        Retrieves and removes the next URL to crawl from the priority queue based on cost.
        """
        async with self.lock:
            if self.priority_queue:
                url_with_cost = heapq.heappop(self.priority_queue)
                return url_with_cost.url
        return None

    async def crawl(self):
        """
        Main crawling loop that manages the scheduling and execution of crawl tasks based on URL costs.
        """
        await self.page_fetcher.init_session()
        await self.add_url(self.base_url, 0)
        tasks = []
        while self.priority_queue or tasks:
            if self.priority_queue and len(tasks)< self.semaphore._value:
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
        Handles completion of a crawl task, logging any exceptions encountered.
        """
        try:
            task.result()
        except Exception as e:
            logging.error(f"Exception caught while processing URL {url}: {e}")

    async def crawl_page(self, url):
        """
        Fetches and processes a single page, following redirects and extracting new URLs to crawl.
        """
        async with self.semaphore:
            try:
                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)
                response_data = await self.page_fetcher.fetch_page(url)  # Adjusted for new return structure
                if response_data['status'] == 'success' and response_data['content']:
                    await self.process_page(response_data, url)
                elif response_data['status'].startswith('redirect') and response_data['new_url']:
                    cost = self.calculate_cost(response_data['new_url'])
                    await self.add_url(response_data['new_url'], cost)
            except aiohttp.ClientError as e:
                self.handle_error(e, url)

    async def process_page(self, response_data, url):
        """
        Processes the content of a fetched page, extracting and enqueuing new URLs to crawl based on their cost.
        """
        logging.info(f"Visiting URL with task_id {self.task_id} : {url}")
        found_links = []
        if response_data['content']:
            # Pass the entire response_data to the parser, assuming it's adjusted to handle such structure
            full_urls = self.page_parser.extract_links_within_domain(response_data, url)
            for full_url in full_urls:
                if full_url not in self.visited_urls:  # Avoid adding duplicates
                    cost = self.calculate_cost(full_url)  # Calculate cost for the new URL
                    await self.add_url(full_url, cost)
                    add_to_found_links(full_url, found_links)

        self.map_url_to_found_links(url, found_links)
        logging.info(f"Links found on {url} with task_id {self.task_id}: {found_links}")

    def calculate_cost(self, url):
        """
        Placeholder for URL cost calculation logic. Cost can be based on factors like link depth, priority, etc.
        """
        return 1  # Placeholder for cost calculation. We will just return one for now and implement further logic based on needs

    def has_more_urls(self):
        """
        Checks if there are more URLs in the priority queue to crawl.
        """
        return bool(self.priority_queue)


# Example usage
task_id = 'example_task_001'  # Optional task ID for tracking
crawler = UniformCostCrawler(base_url="https://monzo.com", task_id=task_id, request_delay=0)

async def main():
    await crawler.crawl()

if __name__ == "__main__":
    asyncio.run(main())
