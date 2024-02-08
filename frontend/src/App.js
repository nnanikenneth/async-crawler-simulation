import React, { useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import TaskInfo from './components/TaskInfo';
import UrlData from './components/UrlData';
import ErrorMessage from './components/ErrorMessage';
import validateUrl from './utils/validateUrl';
import { startCrawl as startCrawlService, checkTaskStatus as checkTaskStatusService } from './services/crawlService';

const VALID_URL_MESSAGE = `Please enter a valid URL ie https://www.monzo.com`
/**
 * The main App component that handles the crawling UI.
 *
 * It allows the user to enter a URL for crawling, validates the URL, starts the crawling process,
 * displays the status of the crawl task, and shows the results once the crawl is completed.
 */
function App() {
  const [startUrl, setStartUrl] = useState(''); // The URL input by the user
  const [taskId, setTaskId] = useState(''); // ID of the crawling task
  const [taskStatus, setTaskStatus] = useState(''); // Status of the crawling task
  const [crawledData, setCrawledData] = useState({}); // Data retrieved from the crawl
  const [loading, setLoading] = useState(false); // Loading state to manage UI feedback
  const [isUrlValid, setIsUrlValid] = useState(true);  // Tracks the validity of the entered URL
  const [errorMessage, setErrorMessage] = useState(''); // Error message state

  /**
   * Handles changes to the URL input field.
   */
  const handleUrlChange = (e) => {
    setStartUrl(e.target.value);
    setIsUrlValid(true); // Assume validity until proven otherwise
  };

   /**
   * Initiates the crawl process when the Enter key is pressed.
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Stop form submission or any default action
      if (validateUrl(startUrl)) {
        setIsUrlValid(true);
        startCrawl();
      } else {
        setIsUrlValid(false);
      }
    }
  };

  /**
   * Starts the crawling process for the entered URL.
   */
  const startCrawl = async () => {
    if (!validateUrl(startUrl)) {
      setIsUrlValid(false);
      setErrorMessage('Invalid URL.'); // Provide immediate feedback for invalid URLs
      return;
    }

    try {
      setLoading(true); // Show loading indicator
      setIsUrlValid(true); // Reset url validity
      setErrorMessage(''); // Clear any existing error messages

      const data = await startCrawlService(startUrl);
      setTaskId(data.task_id); // Store task ID from response
      checkTaskStatus(data.task_id); // Start checking the task status
    } catch (error) {
      console.error("Fetching error:", error.message);
      setErrorMessage(`Network error: ${error.message}`);
      setLoading(false);
    }
  };

  /**
   * Polls the backend service for the status of the crawling task.
   */
  const checkTaskStatus = async (taskId) => {
    const statusInterval = setInterval(async () => {
      try {
        const data = await checkTaskStatusService(taskId);

        setTaskStatus(data.status);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(statusInterval); // Stop polling
          setLoading(false);
          if (data.status === 'completed') {
            setCrawledData(data.crawled_data); // Update state with crawled data
          }
          else {
            setErrorMessage("Task failed."); // Optionally inform the user of failure
          }
        }
      } catch (error) {
        console.error("Fetching error:", error.message);
        setErrorMessage(`Network error: ${error.message}`);
        clearInterval(statusInterval);
        setLoading(false);
      }
    }, 2000); // Poll every 2 seconds
  };


  return (
    <div className="App" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <TextField
          label="Enter URL to crawl"
          variant="outlined"
          value={startUrl}
          onChange={handleUrlChange}
          onKeyPress={handleKeyPress}
          fullWidth
        />

        {<Tooltip title={!isUrlValid && startUrl.length > 0 ? {VALID_URL_MESSAGE} : ""}>
          <span>
            <Button
              variant="contained"
              color="primary"
              onClick={startCrawl}
              // Disable based on loading state, URL validity, and whether input is empty
              disabled={loading || !isUrlValid || startUrl.length === 0} 
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : "Start Crawling"}
            </Button>
          </span>
        </Tooltip>}

      </div>
      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}>
          <CircularProgress />
        </div>
      )}
      {!loading && taskId && (
        <TaskInfo taskId={taskId} status={taskStatus} startUrl={startUrl} />
      )}
      {taskStatus === 'completed' && (
        <div>
          <Typography variant="h6" style={{ marginBottom: '20px' }}>Crawled Data:</Typography>
          {Object.entries(crawledData).map(([url, links], index) => (
            <UrlData key={index} url={url} links={links} />
          ))}
        </div>
      )}
      {!isUrlValid && startUrl.length > 0 && <ErrorMessage message={VALID_URL_MESSAGE} />}
      {errorMessage && <ErrorMessage message={errorMessage} />}
    </div>
  );
}

export default App;
