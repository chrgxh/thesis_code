import requests
import pandas as pd
from loguru import logger

# Base URL of the Flask app
BASE_URL = "http://localhost:8080"  # Change this if the app runs elsewhere

# Endpoint for querying the database
QUERY_ENDPOINT = f"{BASE_URL}/query"

class QueryError(Exception):
    """Custom exception for query failures."""
    def __init__(self, message="The query failed to execute.", *args):
        super().__init__(message, *args)


def query_db_access_api(query_endpoint:str,query_payload:str)->pd.DataFrame:
    try:
        response = requests.post(query_endpoint, json=query_payload)
        
        # Check the response status code
        if response.status_code == 200:
            logger.info(f"Query {query_payload} completed succesfully.")
            if response.json()['success']:
                return pd.DataFrame(response.json()['data'])
            else:
                logger.error(f"Query {query_payload} failed.")
                logger.info(response.text)
                raise QueryError(f"The query failed to execute: {response.json()['error']}")
        else:
            logger.error(f"Query {query_payload} failed.")
            logger.info(response.text)
            raise QueryError(f"The query failed to execute: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    query_payload = {
    "query": "SELECT * FROM device_metadata LIMIT 5;" 
    }
    df=query_db_access_api(QUERY_ENDPOINT,query_payload)
    print(df.head())
    print(df.columns.tolist())