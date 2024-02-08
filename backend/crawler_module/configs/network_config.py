class NetworkConfig:
    """
    Configuration class for network settings of the web crawler.

    This class defines constants used for configuring the HTTP requests made by the crawler, including headers,
    proxy settings, rate limiting, SSL certificate path, connection pooling, and redirect behavior.

    Attributes:
        REQUEST_HEADERS (dict): Headers to be sent with each HTTP request. These headers include the User-Agent,
            Accept, and Accept-Language headers, which can help in making the crawler requests appear more like
            those from a real browser to web servers.

        PROXY_SERVER (str): The URL of the proxy server through which all crawler requests should be routed. This
            is useful for anonymizing requests or for crawling from a specific geographical location.

        PROXY_AUTH (tuple or None): Authentication credentials for the proxy server, if required. Set to a tuple
            of ('username', 'password') or None if no authentication is needed.

        RATE_LIMIT (int): The number of requests per second the crawler is limited to. This rate limiting helps
            in preventing the crawler from overwhelming web servers and getting banned.

        SSL_CERT_PATH (str): The file path to the SSL certificate (.pem file) used for verifying HTTPS connections.
            This can be necessary if the crawler makes requests to servers with self-signed certificates or if
            additional SSL verification is required.

        ENABLE_CONNECTION_POOLING (bool): Flag indicating whether connection pooling should be used. Enabling
            connection pooling can significantly improve crawling efficiency by reusing existing connections
            instead of establishing a new connection for each request.

        FOLLOW_REDIRECTS (bool): Flag indicating whether the crawler should automatically follow HTTP redirects
            (e.g., 301, 302 responses). Enabling this allows the crawler to track content moved to new URLs.
    """

    REQUEST_HEADERS = {
        "User-Agent": "MyCustomWebCrawler/1.0 (+https://mycrawler.com)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en",
    }

    PROXY_SERVER = "http://proxy.example.com:8080"
    PROXY_AUTH = ("username", "password")  # Or use None if no auth is needed

    RATE_LIMIT = 1  # requests per second
    SSL_CERT_PATH = "/path/to/cert.pem"

    ENABLE_CONNECTION_POOLING = True

    FOLLOW_REDIRECTS = True
