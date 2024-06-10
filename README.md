# Async Web Crawler Application

## Overview
This simple web crawler is designed to navigate through a website starting from a given URL, visiting each URL found on the same domain. It efficiently avoids external links to ensure focused crawling within the specified domain. Developed using Python for backend logic and React.js for the frontend interface, this application demonstrates basic web crawling and UI interaction capabilities.

## Features
-  Domain-Specific Crawling : Crawls only within the specified domain, ignoring external links.
- Link Extraction: Identifies and lists links found on each crawled page.
- React.js Frontend: Provides a user-friendly interface to initiate crawls and display results.
- Python Backend: Utilizes async Python scripts for crawling logic and server responses.

## Architecture
The crawler employs a modular architecture to allow customization and extension:

- Crawler Algorithms: Implements the core crawling logic like BFS, DFS strategies, Incremental Crawler and uniform cost crawler algorithms.
- Page Fetcher: Handles HTTP requests, sessions and responses including redirects and retries.
- Page Parser: Extracts links and data from content using BeautifulSoup.
- Middleware: Additional processing logic for filtering, aggregating, rate limiting etc.

## Getting Started
- Dependencies Python 3.8+
- Required Python packages are listed in `requirements.txt`

#### Configuration
The crawler can be configured by modifying files in the config directory ie `network_config.py` and `crawler_config.py`

#### Starting the Application
A bash script is provided to automate the setup process. Run the following command in the project's root directory:

- Note: Ensure that the script has execute permissions. You can do this by running: `chmod +x deploy_production.sh`
```bash
./deploy_script.sh
```

This script sets up both the frontend and backend components, making the application ready to use.

#### Installation & Setup
Follow these steps to get the crawler up and running on your system:

#### Prerequisites
Python 3.8+
Node.js and npm

#### Setting Up the Backend
1. Navigate to the project's root directory.
2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```
#### Start the backend server:
```bash
python3 main.py &
```
This starts the FastAPI application, which listens for incoming crawl requests.

#### Setting Up the Frontend
Navigate to the frontend directory.
Install npm packages:
```bash
npm install
```
#### Build the React app:
```bash
npm run build
```

Optionally, for development purposes, start the React development server:
```bash
npm start
```
Access the frontend application through http://localhost:8000.

## Successful Installation Screenshots
Once you've completed the installation, you should see the application running as shown below:
##### Initial Front Page: 
![Alt text](https://drive.google.com/uc?export=view&id=1xwW5jG0I0QHX6Q9wyplkiilrimg4h_Sl "Initial Front Page")
Shows the list of links that have been crawled by the application.
This screenshot confirms the successful setup and running of the web crawler's user interface.

####  Application Screenshots
To give you a better understanding of the application's functionality, here are screenshots of the UI after initiating a crawl:

##### Crawled Links: 
![Alt text](https://drive.google.com/uc?export=view&id=1rW3zYqsCiZYCpOnq1UAVv02jtvxMRzM8 "Crawled Links Expanded")

##### Crawled Links Expanded: 
![Alt text](https://drive.google.com/uc?export=view&id=1eUuOR9zgzLCSIDcuImj2g01swZX2HWqQ "Crawled Links")

Demonstrates the expanded view of crawled links, providing detailed insights.

## Usage
1. Initiating a Crawl: Use the React.js frontend to enter the starting URL for the crawl.
2. Viewing Results: The frontend displays URLs visited and links found on each page in an expandable format.

## Development Notes
- validateUrl.js: Validates the input URL to ensure it's in the correct format.
- UrlData.js: Displays crawled URLs and associated links using Material UI components.
- webpack.config.js: Configures the webpack for bundling the React.js application.


## Running Tests
Unit tests check key functionality related to the core crawling algorithms, Politeness policies, and utility functions. Run them on the project root directory using:

```bash
 pytest ./tests/
```
OR Just simply
```bash
 pytest 
```
## API Reference

The backend server exposes several endpoints to interact with the web crawler. Below is the documentation for these endpoints.
#### Get Task Status
Retrieves the status of a web crawling task by its ID.
URL
`/task-status/:id`
Method:
`GET`
URL Params
- Required:
`id=[string]`
- Success Response:
  - Code: 200
    Content:
    ```
    {
    "id": "xyz",
    "status": "completed",
    "startUrl": "https://example.com",
    "visitedUrls": ["https://example.com/about", "https://example.com/contact"],
    }

    ```
- Error Response:
  - Code: 404 NOT FOUND
    Content:
    ```json
    {
    "detail": "Task not found."
    }
    ```
 OR
- Code: 500 INTERNAL SERVER ERROR 
Content: `{ error : "Details about the error" }`
- Sample Call:
    ```javascript
    fetch("/task-status/12345")
    .then(response => response.json())
    .then(json => console.log(json))
    .catch(err => console.error("Error:", err));
    ```

#### Start Crawl
Initiates a new web crawling task.

URL
`/start-crawl`
Method:
`POST`
- Data Params
Required:
    ``` json
    {
    "start_url": "https://monzo.com"
    }
    ```
- Success Response:
  - Code: 200 
    Content:
    ```json

    {
    "taskId": "12345",
    "status": "initiated",
    "startUrl": "https://monzo.com"
    }
    ```
- Error Response:
  - Code: 400 BAD REQUEST 
Content: `{ error : "Invalid URL provided" }`
- Sample Call:
    ```javascript
    fetch("/start-crawl", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        start_url: "https://example.com"
    })
    })
    .then(response => response.json())
    .then(json => console.log(json))
    .catch(err => console.error("Error:", err));
    ```

## License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License. <br/>

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
