from fastapi import APIRouter, HTTPException
from models import CrawlRequest
from services.crawl_service import start_crawl, get_task_status

router = APIRouter()

@router.post("/start-crawl/")
async def start_crawl_endpoint(crawl_request: CrawlRequest):
    """
    Initiates a crawling task with the given start URL.

    This endpoint accepts a POST request with a body containing the start URL for crawling. It utilizes the
    CrawlRequest model for request validation. On receiving a valid request, it initiates a crawling task
    and returns the initial response or task identifier.

    Parameters:
        crawl_request (CrawlRequest): A Pydantic model instance containing the `start_url` attribute.

    Returns:
        A JSON response with the task identifier and any other relevant information regarding the initiated crawling task.

    Raises:
        HTTPException: If the crawl request fails to initiate, an HTTPException might be raised with appropriate details.
    """
    return await start_crawl(crawl_request.start_url)


@router.get("/task-status/{task_id}")
async def get_task_status_endpoint(task_id: str):
    """
    Retrieves the status of a previously initiated crawling task by its task ID.

    This endpoint accepts a GET request with a task ID as a path parameter. It checks the status of the specified
    crawling task and returns the current status information. If the task ID is not found or invalid, it raises an
    HTTPException with a 404 status code indicating that the task was not found.

    Parameters:
        task_id (str): The unique identifier of the crawling task whose status is being queried.

    Returns:
        A JSON response containing the current status of the crawling task, which may include status indicators,
        the number of pages crawled, any errors encountered, and so on.

    Raises:
        HTTPException: If the specified task ID does not correspond to any known task, an HTTPException with a 404 status code
        and a detail message "Task not found" is raised.
    """
    task_info = await get_task_status(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_info
