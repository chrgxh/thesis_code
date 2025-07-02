import requests
import pandas as pd
from loguru import logger
from common import *
from tenacity import (
    retry,
    stop_after_attempt,
    wait_chain,
    wait_fixed,
    retry_if_exception_type,
    RetryCallState
)

def loguru_before_sleep(retry_state: RetryCallState) -> None:
    """
    Callback that logs (via Loguru) before each sleep occurs in a retry cycle.
    """
    attempt_number = retry_state.attempt_number
    wait_time = retry_state.next_action.sleep
    exception = retry_state.outcome.exception()
    
    logger.warning(
        f"Retrying (attempt {attempt_number}). "
        f"Waiting {wait_time} seconds. "
        f"Reason: {exception}"
    )

class QueryError(Exception):
    """Custom exception for query failures."""
    def __init__(self, message="The query failed to execute.", *args):
        super().__init__(message, *args)


@retry(
    retry=retry_if_exception_type((requests.exceptions.RequestException, QueryError)),
    wait=wait_chain(wait_fixed(60), wait_fixed(180), wait_fixed(300)),
    stop=stop_after_attempt(4),
    before_sleep=loguru_before_sleep
)
def query_db_access_api(query_payload: str) -> pd.DataFrame:
    response = requests.post(QUERY_ENDPOINT, json=query_payload)

    if response.status_code != 200:
        logger.error(f"Query {query_payload} failed with status code {response.status_code}")
        logger.debug(response.text)
        raise QueryError(f"The query failed to execute: {response.text}")

    json_data = response.json()
    if not json_data.get("success", False):
        logger.error(f"Query {query_payload} failed.")
        logger.debug(response.text)
        raise QueryError(f"The query failed to execute: {json_data.get('error', 'Unknown error')}")

    logger.debug(f"Query {query_payload} completed successfully.")
    return pd.DataFrame(json_data["data"])

if __name__ == '__main__':
    devices="'shellyplug-s-7C87CEBA9A48','domxplug-286BE0','domxem3-349454719423'"
    query = f"""
        SELECT device_id , timestamp , power_data , phase
        FROM device_measurements_30
        WHERE device_id IN ({devices})
          AND "timestamp" >= '2024-02-06 13:42:04+00:00'
          AND "timestamp" < '2024-02-06 13:42:06+00:00'
        ORDER BY "timestamp" ASC;
    """
    query_payload = {"query":query}
    df=query_db_access_api(query_payload)
    logger.info(df.head())
    logger.info(df.columns.tolist())