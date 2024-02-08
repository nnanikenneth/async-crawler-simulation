class CrawlerConfig:
    """
    Configuration settings for a web crawler.

    This class defines various settings that control the behavior of a web crawler. These settings include initial
    URLs to start crawling from, politeness policies such as request delays, user agent rotation, respecting robots.txt,
    handling redirects, domain exclusions, request timeouts, retry strategies, concurrency levels, output formatting,
    and custom data extraction rules.

    Attributes:
        START_URLS (list of str): Initial URLs to start the crawling process.
        MAX_RETRIES (int): Maximum number of retries for a request if it fails.
        DFS_ALGORITHM_MAX_DEPTH (int or float): Maximum depth for depth-first search crawling. Set to float('inf') for no limit.
        REQUEST_DELAY (int): Delay between requests to the same domain, in seconds, to avoid overloading servers.
        FOLLOW_REDIRECTS (bool): Whether the crawler should automatically follow redirects.
        REDIRECTION_STATUS_CODES (list of int): HTTP status codes that indicate a redirect should be followed.
        USER_AGENTS (list of str): List of user agent strings for the crawler to use when making requests.
        ROTATE_USER_AGENT (bool): Whether to rotate user agents for each request.
        RESPECT_ROBOTS_TXT (bool): Whether the crawler should obey robots.txt rules for a site.
        FOLLOW_LINK_PATTERNS (list of str): Regex patterns of URLs that the crawler should follow.
        EXCLUDE_DOMAINS (list of str): Domains or subdomains that the crawler should exclude from crawling.
        REQUEST_TIMEOUT (int): Timeout for HTTP requests, in seconds.
        UNSUPPORTED_CONTENT_TYPES (list of str): MIME types that the crawler should ignore.
        RETRY_BACKOFF_FACTOR (float): Factor by which the delay until the next retry is multiplied.
        RETRY_ON_STATUS (list of int): HTTP status codes on which to retry a request.
        CONCURRENT_REQUESTS (int): Number of concurrent requests the crawler can make.
        MAX_PAGES_TO_CRAWL (int): Maximum number of pages to crawl. Set to limit the scope of the crawl.
        MAX_CRAWL_DURATION (int): Maximum duration of a crawl session, in seconds.
        OUTPUT_FORMAT (str): Format of the output file ('json', 'csv', etc.).
        OUTPUT_DIRECTORY (str): Directory where output files will be saved.
        DATA_EXTRACTION_RULES (dict): Custom rules for extracting data from crawled pages.

    Usage:
        Configure the crawler by modifying these attributes as needed before starting a crawl operation. This allows
        for customizable crawling strategies tailored to specific requirements or politeness policies.
    """
    # Start URLs: Initial list of URLs to start crawling from
    START_URLS = [
        "https://monzo.com",
    ]

    MAX_RETRIES = 2

    # Maximum depth for crawling (depth 0 is the start URLs)
    DFS_ALGORITHM_MAX_DEPTH = float('inf')

    # Delay between requests to the same domain (in seconds) for politeness
    REQUEST_DELAY = 1

    FOLLOW_REDIRECTS = True

    # List of HTTP status codes that indicate redirection
    REDIRECTION_STATUS_CODES = [301, 302, 303, 307, 308]

    # User-Agent string to identify the crawler
    USER_AGENTS = [
        'MyCrawler/1.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0; +http://www.mycrawler.com/info)',
        # Add more user agents as needed
    ]

    # Set to True to rotate user agents, False to use a fixed user agent
    ROTATE_USER_AGENT = False

    # Whether to respect robots.txt rules
    RESPECT_ROBOTS_TXT = True

    # Regex patterns of URLs to follow
    FOLLOW_LINK_PATTERNS = []

    # Domains or subdomains to exclude from crawling
    EXCLUDE_DOMAINS = [
        "https://exclude.example.com",
        "https://subdomain.anotherexample.com"
    ]

    # Request timeout (in seconds)
    REQUEST_TIMEOUT = 10

    # Unsupported content types
    UNSUPPORTED_CONTENT_TYPES = [
        'audio/',
        'application/pdf',
    ]

    RETRY_BACKOFF_FACTOR = 0.5

    RETRY_ON_STATUS = [500, 502, 503, 504]

    # Concurrency settings: Number of threads or processes
    CONCURRENT_REQUESTS = 10

    # Resource limits
    MAX_PAGES_TO_CRAWL = 1000
    MAX_CRAWL_DURATION = 3600  # in seconds (1 hour)

    # Output settings
    OUTPUT_FORMAT = "json"  # Options: 'json', 'csv', etc.
    OUTPUT_DIRECTORY = "crawled_data"

    # Custom settings for data extraction, if needed
    DATA_EXTRACTION_RULES = {
        "article": {
            "title": "h1.article-title",
            "content": "div.article-content"
        }
    }
