import React from 'react';
import Typography from '@mui/material/Typography';

const TaskInfo = ({ taskId, status, startUrl, count }) => (
  <div style={{ margin: '20px 0' }}>
    <Typography variant="body1"><strong>Task ID:</strong> {taskId}</Typography>
    <Typography variant="body1"><strong>Status:</strong> {status}</Typography>
    <Typography variant="body1"><strong>Start URL:</strong> {startUrl}</Typography>
  </div>
);

export default TaskInfo;
