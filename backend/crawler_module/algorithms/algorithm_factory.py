from abc import ABC, abstractmethod

from .bfs_crawler import BFSCrawler 
from .dfs_crawler import DFSCrawler 
from .uniform_cost_crawler import UniformCostCrawler 
from .incremental_crawler import IncrementalCrawler

class AlgorithmFactory:
    """
    A factory class for creating instances of crawling algorithms.

    This class provides a static method to create instances of different crawling algorithms based on their names.
    It abstracts the instantiation process, allowing for easy creation of crawler instances without needing to know
    the specific classes. 

    Attributes:
        None, as this factory class does not maintain state.

    """
    @staticmethod
    def create_algorithm(name, base_url, task_id):
        """
        Create and return an instance of a crawling algorithm based on the given name.

        This method matches the given name to a corresponding crawler class and initializes it with the provided base_url and task_id.
        The method ensures that the correct crawler type is instantiated based on the algorithm name provided. It supports
        breadth-first search (BFS), depth-first search (DFS), incremental, and uniform cost search algorithms.

        Parameters:
            name (str): Name of the algorithm to create. It is case-insensitive and should match one of the supported algorithms ('bfs', 'dfs', 'incremental', 'uniform_cost_search').
            base_url (str): The base URL to start crawling from. This URL serves as the starting point for the crawler.
            task_id (str): A unique identifier for the crawling task. This can be used for tracking or logging purposes.

        Returns:
            BaseCrawler: An instance of a subclass of BaseCrawler, corresponding to the requested algorithm.

        Raises:
            ValueError: If the `name` does not correspond to any known algorithm, this exception is raised with a message indicating the issue.

        Example Usage:
            # To create a BFS crawler instance:
            bfs_crawler = AlgorithmFactory.create_algorithm('bfs', 'https://example.com', 'some_task_id')

            # To create a DFS crawler instance:
            dfs_crawler = AlgorithmFactory.create_algorithm('dfs', 'https://example.com', 'some_task_id')
        """
        if name.lower() == 'bfs':
            return BFSCrawler(base_url, task_id)
        elif name.lower() == 'dfs':
            return DFSCrawler(base_url, task_id)
        elif name.lower() == 'incremental':
            return IncrementalCrawler(base_url, task_id)
        elif name.lower() == 'uniform_cost_search':
            return UniformCostCrawler(base_url, task_id)
        else:
            raise ValueError(f"Unknown algorithm: {name}")

