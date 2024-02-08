from abc import ABC, abstractmethod

class BaseCrawler(ABC):
    """
    Abstract base class for the crawling algorithms.

    This class defines the basic structure and necessary methods that all crawling algorithms should implement.
    It provides a framework for initiating a crawl, adding URLs to the crawl queue, retrieving the next URL,
    processing the content of a page, and checking if more URLs are available for crawling.

    Attributes:
        base_url (str): The starting point URL for the crawling process.
        visited_urls (set): A set to keep track of all visited URLs to avoid revisiting.
        links_to_found_links_map (dict): A dictionary mapping URLs to the links found on those URLs.

    Methods:
        add_url(url: str, cost: Optional[int]): Abstract method to add a URL to the list of URLs to be crawled.
        get_next_url(): Abstract method to retrieve the next URL to be crawled.
        crawl(): Abstract method to start the crawling process.
        process_page(content: str, url: str): Abstract method to process the content of a crawled page.
        has_more_urls(): Abstract method to check if there are more URLs to crawl.
        is_crawling(): Convenience method to check if the crawling process should continue.
        get_crawled_links(): Retrieve the map of URLs to their found links.
        map_url_to_found_links(url: str, links: List[str]): Store the links found on a given URL.
        handle_error(error: Exception, url: str): Handle errors encountered during crawling.
    """
    def __init__(self, base_url, task_id=None):
        """
        Initializes a new crawler instance with a base URL and an optional task ID.

        Parameters:
            base_url (str): The URL to start crawling from.
            task_id (Optional[str]): An identifier for the crawling task, default is None.
        """
        self.base_url = base_url
        self.visited_urls = set()
        self.links_to_found_links_map = {}  # Dictionary to store found links

    @abstractmethod
    def add_url(self, url, cost=None):
        """
        Add a URL to the list of URLs to be crawled.
        If 'cost' is provided, it is used in the context of a uniform cost crawler.

        Parameters:
            url (str): The URL to add to the crawl queue.
            cost (Optional[int]): The cost associated with crawling this URL, if applicable.
        """
        pass

    @abstractmethod
    def get_next_url(self):
        """
        Retrieve the next URL to crawl.

        Returns:
            str: The next URL to be crawled.
        """
        pass

    @abstractmethod
    def crawl(self):
        """
        Start the crawling process. This method provides the basic flow of crawling.
        Implement this method in each crawler subclass to define specific crawling behavior.
        """
        pass

    @abstractmethod
    def process_page(self, content, url):
        """
        Process the content of a page.

        Parameters:
            content (str): The content of the page that was crawled.
            url (str): The URL of the page whose content is being processed.
        """
        pass

    @abstractmethod
    def has_more_urls(self):
        """
        Check if there are more URLs to crawl.

        Returns:
            bool: True if there are more URLs to crawl, False otherwise.
        """
        pass
    
    def is_crawling(self):
        """
        Check if the crawling process should continue based on the availability of more URLs.

        Returns:
            bool: True if there are more URLs to crawl, False otherwise.
        """
        return self.has_more_urls()
    
    def get_crawled_links(self):
        """
        Retrieve the map of URLs to the links found on those URLs.

        Returns:
            dict: A dictionary mapping each crawled URL to a list of links found on that URL.
        """
        return self.links_to_found_links_map
    
    def map_url_to_found_links(self, url, links):
        """
        Store the links found on the given URL.

        Parameters:
            url (str): The URL where links were found.
            links (list of str): The links found on the given URL.
        """
        self.links_to_found_links_map[url] = links

    def handle_error(self, error, url):
        """
        Handles errors encountered during crawling by categorizing and logging them.

        Parameters:
            error (Exception): The error encountered during the crawling process.
            url (str): The URL at which the error was encountered.

        Outputs:
            Error message indicating the nature of the error and the URL at which it occurred.
        """
        error_handlers = {
            HTTPError: lambda error, url: logging.error(f"HTTP error encountered for {url}: {error}"),
            ConnectionError: lambda error, url: logging.warning(f"Connection error for {url}: {error}"),
            # add any error types you wish to handle
        }

        handler = error_handlers.get(type(error), lambda error, url: logging.error(f"Unexpected error for {url}: {error}"))
        handler(error, url)
