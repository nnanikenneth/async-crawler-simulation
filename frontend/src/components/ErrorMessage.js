import React from 'react';

const ErrorMessage = ({ message }) => (
  <div style={{ marginTop: '10px', color: 'red', fontSize: '0.875rem' }}>
    {message}
  </div>
);

export default ErrorMessage;
