# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size
# --upgrade pip: Ensures we have the latest version of pip
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run the application
# Use gunicorn as the production server with uvicorn workers
# -w 4: Spawns 4 worker processes
# -k uvicorn.workers.UvicornWorker: Uses the uvicorn worker class for asyncio compatibility
# -b 0.0.0.0:8000: Binds the server to all network interfaces on port 8000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "api.index:app", "-b", "0.0.0.0:8000"]