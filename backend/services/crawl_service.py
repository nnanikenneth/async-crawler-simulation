import uuid
import asyncio
from crawler_module.algorithms.algorithm_factory import AlgorithmFactory
from service_configs.settings import DEFAULT_ALGORITHM
from fastapi import HTTPException

tasks = (
    {}
)  # A global dictionary to store task information. (We could use a persistent database or in-memory cache)


async def start_crawl(start_url):
    """
    Asynchronously initiates a web crawling task using a specified starting URL.

    This function generates a unique task ID for the new crawling task, creates a crawler instance using the default
    algorithm specified in the configuration, and then starts the crawl asynchronously. Information about the task,
    including its ID, status, and crawler instance, is stored in a global dictionary.

    Parameters:
        start_url (str): The URL from which the crawling task should start.

    Returns:
        dict: A dictionary containing the task ID and a message indicating that the crawling has started, along with the
        algorithm used and the starting URL.

    Raises:
        None directly, but the function may indirectly raise exceptions through the crawling process or task creation.
    """
    task_id = str(uuid.uuid4())
    default_algorithm = DEFAULT_ALGORITHM

    crawler = AlgorithmFactory.create_algorithm(default_algorithm, start_url, task_id)
    # Asynchronously start the crawling process and assign it a name based on the task ID.
    task = asyncio.create_task(crawler.crawl(), name=f"CrawlTask-{task_id}")

    # Store task details in the global tasks dictionary.
    tasks[task_id] = {
        "task": task,
        "status": "running",
        "start_url": start_url,
        "crawler": crawler,
    }
    return {
        "task_id": task_id,
        "message": f"Crawling started with {default_algorithm.upper()} for {start_url}",
    }


async def get_task_status(task_id):
    """
    Asynchronously retrieves the status of a specified crawling task by its task ID.

    This function looks up the task in the global dictionary using the provided task ID. If the task is found, it
    checks whether the task is still running or has completed and returns the current status along with any data
    collected by the crawler.

    Parameters:
        task_id (str): The unique identifier of the crawling task whose status is being queried.

    Returns:
        dict: A dictionary containing the task ID, status, start URL, and any crawled data collected so far. If the task
        is completed, 'crawled_data' will contain the links found; otherwise, it will be empty.

    Raises:
        HTTPException: If no task with the given task ID exists, an HTTPException with a 404 status code and a detail
        message "Task not found" is raised.
    """
    task_info = tasks.get(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_info["task"]
    if task.done():
        # Update the task status based on whether an exception occurred.
        task_info["status"] = "completed" if task.exception() is None else "failed"
        # Retrieve crawled data from the crawler instance.
        crawled_data = task_info["crawler"].get_crawled_links()

        return {
            "task_id": task_id,
            "status": task_info["status"],
            "start_url": task_info["start_url"],
            "crawled_data": crawled_data,
        }
    else:
        # If the task is still running, return the current status without crawled data.
        return {
            "task_id": task_id,
            "status": task_info["status"],
            "start_url": task_info["start_url"],
            "crawled_data": {},
        }

