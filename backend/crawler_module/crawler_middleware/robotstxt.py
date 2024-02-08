import asyncio
from urllib.parse import urlparse, urljoin
from aiohttp import ClientError
from urllib.robotparser import RobotFileParser
from io import StringIO
import aiohttp

class RobotsTxt:
    """
    The RobotsTxt class is responsible for managing and enforcing rules specified in robots.txt files
    for different domains. It provides functionality to check if a given URL can be fetched based
    on these rules.

    This class fetches and parses the robots.txt file for a domain (if it exists) and caches the
    parsed rules. Subsequent checks for URLs under the same domain use this cache, reducing the
    number of network requests.

    If a robots.txt file cannot be fetched (e.g., due to network issues or if the file doesn't exist),
    this class assumes no restrictions on crawling for that domain.

    Usage:
        robots_txt = RobotsTxt()
        is_allowed = robots_txt.is_fetch_allowed(user_agent, url)

        if is_allowed:
            # Proceed with fetching the URL
        else:
            # Avoid fetching the URL as per robots.txt restrictions

    Attributes:
        parsers (dict): A dictionary to cache RobotFileParser instances for each domain.
        no_robots_txt (set): A set to keep track of domains without a robots.txt file.

    Methods:
        get_or_create_parser(base_url): Retrieves or creates a RobotFileParser for the given base URL.
        is_fetch_allowed(user_agent, url): Checks if a URL is allowed to be fetched for the given user agent as per robots.txt rules.
    """

    def __init__(self, session):
        self.session = session  # Use the passed aiohttp.ClientSession
        self.parsers = {}  # Cache for RobotFileParser instances
        self.no_robots_txt = set()  # Remember domains without robots.txt

    async def fetch_robots_txt(self, robots_txt_url):
        """Asynchronously fetch and return the content of robots.txt using the provided session."""
        try:
            async with self.session.get(robots_txt_url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None
        except ClientError:
            return None

    async def get_or_create_parser(self, base_url):
        """Get the existing parser for a base URL or create a new one if not present."""
        if base_url not in self.parsers and base_url not in self.no_robots_txt:
            robots_txt_url = urljoin(base_url, "robots.txt")
            content = await self.fetch_robots_txt(robots_txt_url)
            if content:
                parser = RobotFileParser()
                parser.parse(StringIO(content).readlines())
                self.parsers[base_url] = parser
            else:
                self.no_robots_txt.add(base_url)
        return self.parsers.get(base_url)

    async def is_fetch_allowed(self, user_agent, url):
        """Check if the given URL is allowed to be fetched according to robots.txt rules."""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        parser = await self.get_or_create_parser(base_url)
        if parser:
            return parser.can_fetch(user_agent, url)
        else:
            return True


# Example usage
"""
async def main():
    async with aiohttp.ClientSession() as session:
        robots_txt = RobotsTxt(session)
        url = "https://www.monzo.com"
        user_agent = "ExampleCrawlerUserAgent/1.0"
        is_allowed = await robots_txt.is_fetch_allowed(user_agent, url)
        if is_allowed:
            print("Fetching is allowed.")
        else:
            print("Fetching is disallowed.")

if __name__ == "__main__":
    asyncio.run(main())
"""
