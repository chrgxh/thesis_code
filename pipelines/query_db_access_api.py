import requests
import pandas as pd
from loguru import logger
from common import *

class QueryError(Exception):
    """Custom exception for query failures."""
    def __init__(self, message="The query failed to execute.", *args):
        super().__init__(message, *args)


def query_db_access_api(query_payload:str)->pd.DataFrame:
    try:
        response = requests.post(QUERY_ENDPOINT, json=query_payload)
        
        # Check the response status code
        if response.status_code == 200:
            logger.debug(f"Query {query_payload} completed succesfully.")
            if response.json()['success']:
                return pd.DataFrame(response.json()['data'])
            else:
                logger.error(f"Query {query_payload} failed.")
                logger.debug(response.text)
                raise QueryError(f"The query failed to execute: {response.json()['error']}")
        else:
            logger.error(f"Query {query_payload} failed.")
            logger.debug(response.text)
            raise QueryError(f"The query failed to execute: {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    query_payload = {
    "query": "SELECT * FROM device_metadata LIMIT 5;" 
    }
    df=query_db_access_api(query_payload)
    logger.info(df.head())
    logger.info(df.columns.tolist())