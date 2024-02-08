#!/bin/bash
# Navigate to the frontend directory and build the React app
cd frontend || exit
npm install
npm run build

# Navigate to the backend directory
cd ../backend || exit

# Install Python dependencies
pip3 install -r requirements.txt

# Start FastAPI app with Uvicorn using main.py
# No need to run Uvicorn separately here since it's invoked in main.py
python3 main.py &

echo "React and FastAPI applications are now running in production mode."

# Note: The FastAPI application is configured to run on localhost (127.0.0.1) at port 8000.
# This means the API will be accessible via http://127.0.0.1:8000 in your web browser.
# Adjust the 'host' and 'port' parameters in main.py if you need to run the server on a different IP or port.
# The `reload=True` option is used for development purposes, allowing the server to automatically reload upon code changes.
# For production deployments, consider removing the `reload=True` option for improved performance and stability.
