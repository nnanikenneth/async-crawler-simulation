from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.crawl_router import router as crawl_router
from service_configs.cors import add_cors_middleware

app = FastAPI()

app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")
"""
Mounts a static files directory to the FastAPI application. This allows the application to serve static files
from a specified directory, making it accessible via the '/static' route. This is typically used to serve
frontend assets such as HTML, CSS, and JavaScript files.

Parameters:
    "/static": The path where the static files will be accessible from.
    StaticFiles(directory="../frontend/dist"): The StaticFiles instance configured with the directory
        containing the static files to serve.
    name="static": An optional name given to this particular static files configuration.
"""


@app.get("/")
async def read_index():
    """
    An endpoint that returns the index.html file from the static files directory.

    This function serves as the main entry point to the frontend application, returning the 'index.html' file
    when the root URL is accessed. It ensures that the SPA (Single Page Application) can be loaded by browsers.

    Returns:
        FileResponse: An HTTP response object that sends the specified file as a response.
    """
    return FileResponse("../frontend/dist/index.html", media_type="text/html")


add_cors_middleware(app)
"""
Configures the FastAPI application with CORS middleware, allowing or restricting cross-origin requests
based on the settings defined in the `add_cors_middleware` function. This is crucial for web applications
that need to accept requests from web pages hosted on different origins.

Note: As the comment in the code suggests, the specific configuration for CORS might not be necessary
anymore depending on the deployment or development setup. It's important to review CORS requirements
as part of security and functionality considerations.
"""

# Include the crawl router in the main application.
app.include_router(crawl_router)
"""
Includes the crawling-related routes defined in `crawl_router` into the main FastAPI application.
This allows the application to handle API requests related to web crawling tasks, such as starting
a crawl or checking the status of a crawl task, by delegating requests to the router.
"""
if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn, an ASGI server, on localhost port 8000.
    # The `reload=True` option enables automatic reloading of the server on code changes.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
