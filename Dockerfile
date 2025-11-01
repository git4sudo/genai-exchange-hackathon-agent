# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install production dependencies.
COPY requirements.txt .
# Install the minimal set of packages needed for FastAPI and BigQuery
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Cloud Run services must listen on the port specified by the PORT environment variable.
# We use uvicorn to run the FastAPI application.
ENV PORT 8080

# Run the web service using Uvicorn. 
# --host 0.0.0.0 ensures it binds to the port provided by Cloud Run.
# app:app refers to the FastAPI instance named 'app' in the 'app.py' file.
# The --workers 1 is appropriate for Cloud Run's typical single-process, highly concurrent nature.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
