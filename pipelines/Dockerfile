# Base image with Python
FROM python:3.8-slim

# Install PostgreSQL client libraries (for pg_config) and a compiler toolchain
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy your script into the container
COPY . .

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your pipeline script by default
CMD ["python", "run_pipeline.py"]
