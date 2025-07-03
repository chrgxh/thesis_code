# Base image with Python
FROM python:3.8-slim

# Install PostgreSQL client libraries (for pg_config) and a compiler toolchain
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY db_access.py db_access.py
COPY csv_loader.py .

# Create the logs directory
RUN mkdir -p /app/logs

# Expose the Flask port
EXPOSE 5000

# Run the script
CMD ["python", "db_access.py"]
