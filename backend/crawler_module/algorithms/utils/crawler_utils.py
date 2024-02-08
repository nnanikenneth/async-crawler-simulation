from urllib.parse import urljoin, urlparse


def normalize_url(base_url, url):
    """
    Normalize a URL by resolving it against a base URL.

    This function takes a base URL and a potentially relative URL and combines them to form a complete, absolute URL.
    It is particularly useful for converting relative URLs found in web pages to absolute URLs that can be requested.

    Args:
        base_url (str): The base URL to resolve against.
        url (str): The URL that needs to be normalized, which can be absolute or relative.

    Returns:
        str: The normalized URL as an absolute URL.

    Examples:
        - If base_url is "http://example.com/section/" and url is "article1.html",
          the function returns "http://example.com/section/article1.html".
        - If base_url is "http://example.com/section/subsection/" and url is "../article2.html",
          the function returns "http://example.com/section/article2.html".
    """
    return urljoin(base_url, url)


def extract_domain(url):
    """
    Extract the domain (netloc) from a given URL.

    This function parses a URL and returns the network location part of it, which usually contains
    the domain name and optionally the port.

    Args:
        url (str): The URL from which the domain needs to be extracted.

    Returns:
        str: The domain (network location) part of the URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc


def is_same_domain(url1, url2):
    """
    Check if two URLs belong to the same domain.

    This function is useful for comparing if two URLs are part of the same site based on their domains.

    Args:
        url1 (str): The first URL to compare.
        url2 (str): The second URL to compare.

    Returns:
        bool: True if both URLs belong to the same domain, False otherwise.
    """
    return extract_domain(url1) == extract_domain(url2)


def add_to_found_links(url, found_links):
    """
    Add a URL to a list of found links.

    This function appends a URL to a given list. It's useful for tracking links found during web scraping or crawling.

    Args:
        url (str): The URL to be added to the list.
        found_links (list): The list of found links. This list will be modified in place.
    """
    found_links.append(url)


def write_to_file(url, links, output_file):
    """
    Write visited URL and found links to a file.

    This function logs a visited URL and its corresponding found links to an output file, appending each entry.
    It's useful for keeping a record of web crawling results for testing.

    Args:
        url (str): The visited URL to log.
        links (list): A list of URLs (links) found at the visited URL.
        output_file (str): Path to the output file where the log should be written.
    """
    with open(output_file, "a") as file:
        file.write(f"Visited: {url}\n")
        file.write("Found links:\n")
        for link in links:
            file.write(f"  - {link}\n")
        file.write("\n")
