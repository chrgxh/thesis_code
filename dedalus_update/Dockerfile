FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variable so Python doesn’t buffer output
ENV PYTHONUNBUFFERED=1

CMD ["python", "update_db_pipeline.py"]
