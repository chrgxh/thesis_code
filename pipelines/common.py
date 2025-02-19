DATA_DIR=r'D:\thesis_code\my_code\pipelines\data'
METADATA_DIR = r'D:\thesis_code\my_code\pipelines\metadata'
JSON_PATH=r'D:\thesis_code\my_code\pipelines\buildings.json'

# Base URL of the Flask app
BASE_URL = "http://localhost:8080"  # Change this if the app runs elsewhere
# BASE_URL = "http://dedalus.epu.ntua.gr:8080/"  # Change this if the app runs elsewhere

# Endpoint for querying the database
QUERY_ENDPOINT = f"{BASE_URL}/query"