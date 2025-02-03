# Base image with Python
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy your script into the container
COPY . .

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your pipeline script by default
CMD ["python", "run_pipeline.py"]
