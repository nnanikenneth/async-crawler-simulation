import aiohttp
import asyncio
import backoff
from ...configs.network_config import NetworkConfig
from ...configs.crawler_config import CrawlerConfig
from ...crawler_middlewares.robotstxt import RobotsTxt
import random

class PageFetcher:
    """
    PageFetcher Class:

    This class designed for asynchronous web page fetching with features tailored for web scraping.

    Provides:
    - User agent rotation to mimic different browsers and reduce the chance of being blocked.
    - Automatic retries on HTTP errors, leveraging exponential backoff.
    - Option to follow HTTP redirects, with compliance checks against robots.txt.

    Methods:
    - set_current_user_agent(): Sets the current user agent based on an index and user agent list.
    - rotate_user_agent(): Rotates the user agent string if user agent rotation is enabled.
    - fetch_page(url): Fetches a web page at the specified URL.
    - Checks if the robotstxt allows crawling with the current user agent.
    - Sends an HTTP GET request with the specified user agent and configurable timeout.
    - Handles HTTP redirections based on configuration.
    - Returns the HTTP response and redirection URL if applicable.
    - Raises an exception for HTTP errors.

    Note:
    Session management (opening and closing) is the responsibility of the user of this class to
    allow for flexible and efficient use of network resources, especially in applications requiring
    long-lived or numerous asynchronous operations.

    Usage:
    - Initialize the PageFetcher.
    - Manually manage the session lifecycle with init_session() and close_session().
    - Use fetch_page() to asynchronously fetch web pages.
    """

    def __init__(self):
        """
        Initializes the PageFetcher with configurations from network and crawler settings.
        """
        self.rate_limit = NetworkConfig.RATE_LIMIT
        self.user_agents = CrawlerConfig.USER_AGENTS
        self.user_agent_index = 0
        self.rotate_user_agent_flag = CrawlerConfig.ROTATE_USER_AGENT
        self.user_agent = random.choice(self.user_agents)
        self.session = (
            None  # Session will be initialized by the external caller in init_session
        )
        self.robots_txt = None  # Will be initialized after session creation

    async def init_session(self):
        """
        Initializes the aiohttp ClientSession for use in subsequent fetch operations.
        This method should be called before any fetch operations to ensure a session is available.
        """
        # Create the ClientSession that will be reused for all fetch operations
        self.session = aiohttp.ClientSession()
        self.robots_txt = RobotsTxt(self.session)

    async def configure_session(self):
        """
        Configures the session with custom retry and status code handling settings.
        This method can be expanded based on specific requirements for status codes or other session parameters.
        """
        self.session.headers.update({"Custom-Header": "Value"})

    async def close_session(self):
        """
        Closes the aiohttp ClientSession gracefully.
        This method should be called after all fetch operations are complete to free network resources.
        """
        # Gracefully close the ClientSession
        if self.session:
            await self.session.close()

    async def set_current_user_agent(self):
        """
        Sets the current user agent from the list of user agents based on the current index.
        This method is used internally to update the user agent when rotating.
        """
        self.user_agent = self.user_agents[self.user_agent_index]

    async def rotate_user_agent(self):
        """
        Rotates the user agent by updating the index to the next user agent in the list.
        This method provides a simple mechanism to avoid detection as a web crawler.
        """
        if self.rotate_user_agent_flag:
            self.user_agent_index = (self.user_agent_index + 1) % len(self.user_agents)
            await self.set_current_user_agent()

    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientError,
        max_tries=2,
        giveup=lambda e: not isinstance(e, aiohttp.ClientError),
    )
    async def fetch_page(self, url):
        """
        Fetches a web page asynchronously.

        Args:
            url (str): The URL of the web page to fetch.

        Returns:
            dict: A dictionary containing the fetch status and content, along with other metadata like new_url and content_type.

        Raises:
            aiohttp.ClientError: If an HTTP client error occurs during the fetch operation.
        """
        if not self.session:
            await self.init_session()

        if not await self.robots_txt.is_fetch_allowed(self.user_agent, url):
            return {
                "content": None,
                "new_url": None,
                "content_type": None,
                "status": "disallowed",
            }

        headers = {"User-Agent": self.user_agent}
        try:
            async with self.session.get(
                url,
                headers=headers,
                timeout=CrawlerConfig.REQUEST_DELAY,
                allow_redirects=CrawlerConfig.FOLLOW_REDIRECTS,
            ) as response:
                content_type = response.headers.get("Content-Type", "")

                if any(
                    unsupported in content_type
                    for unsupported in CrawlerConfig.UNSUPPORTED_CONTENT_TYPES
                ):
                    return {
                        "content": None,
                        "new_url": None,
                        "content_type": content_type,
                        "status": "skipped",
                    }
                elif (
                    response.status in CrawlerConfig.REDIRECTION_STATUS_CODES
                    and "Location" in response.headers
                ):
                    new_url = response.headers["Location"]
                    return {
                        "content": None,
                        "new_url": new_url,
                        "content_type": content_type,
                        "status": "redirect",
                    }
                elif response.status >= 200 and response.status < 300:
                    # Getting raw content as bytes
                    content = await response.read()
                    return {
                        "content": content,
                        "new_url": None,
                        "content_type": content_type,
                        "status": "success",
                    }
                else:
                    return {
                        "content": None,
                        "new_url": None,
                        "content_type": content_type,
                        "status": f"error_{response.status}",
                    }
        except aiohttp.ClientError as e:
            return {
                "content": None,
                "new_url": None,
                "content_type": None,
                "status": "client_error",
            }


# Example usage
async def main():
    # URL to fetch
    url_to_fetch = "http://monzo.com"

    # Create an instance of PageFetcher
    fetcher = PageFetcher()

    # Initialize session
    await fetcher.init_session()

    # Optionally rotate the user agent
    await fetcher.rotate_user_agent()

    # Fetch the page
    response = await fetcher.fetch_page(url_to_fetch)

    print(f"Fetch status: {response['status']}")

    if response['status'] == 'success':
        # Handle successful fetch, e.g., process response['content']
        print("Page fetched successfully.")
    else:
        # Handle other statuses, including redirects, errors, and unsupported content types
        print(f"Page fetch was not successful: {response['status']}")

    # session is closed properly
    await fetcher.close_session()

# Run the main function in the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())

