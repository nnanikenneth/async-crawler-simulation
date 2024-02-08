/**
 * Configuration and utility functions to interact with the web crawler backend.
 */

// Base URL for the backend server.
const BACKEND_BASE_URL = `http://localhost:8000`;

/**
 * Initiates a web crawl operation by sending a POST request to the backend.
 *
 * This function sends a request to the backend to start a new web crawling task
 * with the provided start URL. It uses the `/start-crawl` endpoint of the backend service.
 *
 * @param {string} startUrl - The starting URL for the web crawl operation.
 * @returns {Promise<object>} A promise that resolves with the response from the backend,
 * indicating the task initiation status and details.
 * @throws {Error} Throws an error if the HTTP request fails or the backend service returns a non-OK status.
 */
const startCrawl = async (startUrl) => {
  const apiUrl = `${BACKEND_BASE_URL}/start-crawl`;
  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      start_url: startUrl,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
};

/**
 * Checks the status of an ongoing web crawl task by task ID.
 *
 * This function queries the backend for the current status of a web crawling task
 * using the `/task-status/{taskId}` endpoint. It is designed to poll the status of a
 * task to update the UI or take action based on the task's progress or completion.
 *
 * @param {string} taskId - The unique identifier of the web crawl task to check.
 * @returns {Promise<object>} A promise that resolves with the task status information
 * from the backend, including progress, any errors encountered, and completion status.
 * @throws {Error} Throws an error if the task is not found (404) or for any other non-OK HTTP status.
 */
const checkTaskStatus = async (taskId) => {
  const response = await fetch(`${BACKEND_BASE_URL}/task-status/${taskId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Task not found.");
    }
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
};

export { startCrawl, checkTaskStatus };
