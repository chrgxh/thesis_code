import pandas as pd
import pytz
import os
import multiprocessing as mp
from loguru import logger
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from pipeline_config_manager import read_config_values,update_last_updated
import multiprocessing
import requests
import io
import sys
from heron_manager import get_device_info, TIME_FORMAT, get_heron_device_data, get_nano_time_from_time_string
from processing import flatten_payload_to_csv_buffer, preview_csv_buffer
from json import JSONDecodeError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_chain,
    wait_fixed,
    retry_if_exception_type,
    RetryCallState
)

# This will show logs in the terminal (stdout)
logger.add(sink=sys.stdout, level="INFO")

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

def init_worker_logger():
    # You could configure sinks, level, etc. here in the child process
    logger.add(f"worker_{os.getpid()}.log")
    return logger

@retry(
    retry=retry_if_exception_type((requests.exceptions.RequestException)),
    wait=wait_chain(wait_fixed(60), wait_fixed(180), wait_fixed(300)),
    stop=stop_after_attempt(4),
    before_sleep=loguru_before_sleep
)
def post_csv_buffer(buffer):
    buffer.seek(0)
    binary_buf = io.BytesIO(buffer.getvalue().encode("utf-8"))
    query_url = "http://localhost:8080/upload_csv"
    resp = requests.post(query_url, files={
        # the tuple is: (filename, fileobj, content_type)
        "file": ("readings.csv", buffer, "text/csv")
        })
    resp.raise_for_status()
    logger.info(resp)
    logger.info(resp.text)

@retry(
    retry=retry_if_exception_type((requests.exceptions.RequestException)),
    wait=wait_chain(wait_fixed(60), wait_fixed(180), wait_fixed(300)),
    stop=stop_after_attempt(4),
    before_sleep=loguru_before_sleep
)
def get_device_period_data(device_id:str,window_start:datetime,window_end:datetime)->dict:
    start_time=window_start.strftime(TIME_FORMAT)
    end_time=window_end.strftime(TIME_FORMAT)
    start_time_ns=get_nano_time_from_time_string(start_time)
    end_time_ns=get_nano_time_from_time_string(end_time)
    return get_heron_device_data(device_id,start_time_ns,end_time_ns)

def create_device_period_csv_buffer(data:dict,device_id:str):
    buffer=flatten_payload_to_csv_buffer(data,device_id)
    logger.info(preview_csv_buffer(buffer).to_string())
    return buffer

def process_device_period(device_id: str, window_start: datetime, window_end: datetime):
    try:
        logger.info(f"Downloading data for device: {device_id} in window: {window_start.isoformat()} → {window_end.isoformat()}")
        
        try:
            data = get_device_period_data(device_id, window_start, window_end)
        except JSONDecodeError as e:
            logger.warning(f"Initial fetch failed with exception: {e}. Data might be too large for device: {device_id} in window: {window_start.isoformat()} → {window_end.isoformat()}. Attempting 5-part split fallback...")
            delta = (window_end - window_start) / 5
            data = []
            for i in range(5):
                part_start = window_start + i * delta
                part_end = window_start + (i + 1) * delta
                try:
                    part_data = get_device_period_data(device_id, part_start, part_end)
                    if part_data:
                        data.extend(part_data)
                except Exception as split_e:
                    logger.warning(f"Split fetch failed for part {i+1}/5: {split_e}")

        if not data:
            logger.warning(f"No data found for device: {device_id} in window: {window_start.isoformat()} → {window_end.isoformat()}")
            return

        logger.info(f"Processing data for device: {device_id} in window: {window_start.isoformat()} → {window_end.isoformat()}")
        buffer = create_device_period_csv_buffer(data, device_id)

        logger.info(f"Uploading data for device: {device_id} in window: {window_start.isoformat()} → {window_end.isoformat()}")
        post_csv_buffer(buffer)

        logger.success(f"Successfully uploaded data for device: {device_id} in window: {window_start.isoformat()} → {window_end.isoformat()}")

    except Exception as e:
        logger.error(f"✗ {device_id} {window_start.strftime(TIME_FORMAT)} EXC: {e}")
        raise e


def run_pipeline():
    last_updated, num_processes, relative_delta = read_config_values()
    current = last_updated
    now_utc = datetime.now(timezone.utc)

    devices = get_device_info()
    if not devices:
        logger.error("No devices found.")
        return

    while current < now_utc:
        window_start = current
        window_end = current + relative_delta

        logger.info(f"\n Processing window: {window_start.isoformat()} → {window_end.isoformat()}")

        tasks = [(device[0], window_start, window_end) for device in devices if device[1] <= window_start ]

        # Parallel processing for this time window
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.starmap_async(process_device_period, tasks).get()  # raises on first error


        # for r in results:
        #     logger.info(r)

        # Update last_updated after all devices for the window are done
        logger.success(f"Successfully fetched data up to {window_end.isoformat()}")
        update_last_updated(new_dt=window_end)

        current = window_end


if __name__ == "__main__":
    run_pipeline()
