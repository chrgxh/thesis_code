import pandas as pd
import pytz
import os
import multiprocessing as mp
from loguru import logger
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from pipeline_config_manager import read_config_values,update_last_updated
import multiprocessing
from tqdm import tqdm
import requests
import io
from heron_manager import get_device_info, TIME_FORMAT, get_heron_device_data, get_nano_time_from_time_string
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

def create_device_period_csv_buffer(data:dict):
    pass

def process_device_period(device_id:str,window_start:datetime,window_end:datetime):
    try:
        # Simulate data processing
        processed_data = {
            "device_id": device_id,
            "from_date": month_start.isoformat(),
            "to_date": month_end.isoformat(),
            "metrics": {
                "total_energy": 123.45,
                "peak_usage": 10.2
            }
        }

        # POST to API
        res = requests.post(f"http://localhost:8000/api/insert", json=processed_data)
        if res.status_code == 200:
            return f"✓ {device_id} {window_start.strftime(TIME_FORMAT)}"
        else:
            return f"✗ {device_id} {window_end.strftime(TIME_FORMAT)} ERR {res.status_code}"
    except Exception as e:
        return f"✗ {device_id} {window_start.strftime(TIME_FORMAT)} EXC: {e}"

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

        print(f"\n📅 Processing window: {window_start.isoformat()} → {window_end.isoformat()}")

        tasks = [(device, window_start, window_end) for device in devices]

        # Parallel processing for this time window
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = list(tqdm(pool.imap_unordered(process_device_period, tasks), total=len(tasks)))

        for r in results:
            print(r)

        # Update last_updated after all devices for the window are done
        update_last_updated(new_dt=window_end)

        current = window_end


if __name__ == "__main__":
    run_pipeline()
