import pandas as pd
import pytz
import os
import multiprocessing as mp
from loguru import logger
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from query_db_access_api import query_db_access_api
from transformations import *
from common import *
from buildings_json_handler import yield_home_map_and_last_updated, update_building_last_updated
from get_metadata import get_device_metadata

def get_data_for_device_in_period(devices: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()

    query = f"""
        SELECT device_id , timestamp , power_data , phase
        FROM device_measurements_30
        WHERE device_id IN ({devices})
          AND "timestamp" >= '{start_str}'
          AND "timestamp" < '{end_str}'
        ORDER BY "timestamp" ASC;
    """
    return query_db_access_api({"query": query})

def process_building(file_count: int, home_id: str, last_updated: str, device_map: str, 
                     relative_time_delta: relativedelta, default_start_date: datetime, tzinfo):
    
    logger.info(f"Starting processing for home: {home_id} (File {file_count})")

    devices_str = ",".join(f"'{key}'" for key in device_map.keys())

    start_date = datetime.fromisoformat(last_updated) + timedelta(seconds=1) if last_updated else default_start_date

    while start_date <= datetime.now(tzinfo):
        end_date = start_date + relative_time_delta
        logger.info(f"Querying data from {start_date} to {end_date} for home: {home_id}")

        df = get_data_for_device_in_period(devices_str, start_date, end_date)
        if df.empty:
            logger.warning(f"No data found for {home_id} between {start_date} and {end_date}.")
            start_date = end_date
            continue
        
        logger.info(f"Retrieved {len(df)} rows for home: {home_id}")

        df = apply_transformations(
            df,
            remove_milliseconds,
            (map_device_id, device_map),
            aggregate_power,
            (reshape_power_data, len(device_map.keys()))
        )

        file_path = fr'{DATA_DIR}\combined_main_and_meters_{file_count}.csv'
        df.to_csv(
            file_path, 
            mode='a',  # Append mode
            index=False, 
            header=not os.path.exists(file_path)  # Write header only if file does not already exist
        )

        updated_at: datetime = df.iloc[-1]['timestamp'].to_pydatetime()
        update_building_last_updated(home_id, updated_at.isoformat())

        logger.info(f"Finished processing batch for home: {home_id}")
        start_date = end_date  # Move to next batch

    logger.info(f"Completed processing for home: {home_id}")

def run_pipeline():
    utc = pytz.UTC
    default_start_date = datetime(2021, 1, 1, 0, 0, 0, tzinfo=utc)
    relative_time_delta = relativedelta(months=1)

    # Collect all buildings to process
    home_data = list(yield_home_map_and_last_updated())
    if not home_data:
        logger.error("No buildings found! Exiting pipeline.")
        return

    logger.info(f"Found {len(home_data)} buildings. Using up to {MAX_PROCESSES} parallel processes.")

    # Prepare arguments for starmap (precompute file_count based on list order)
    args = [(i + 1, home_id, last_updated, device_map, relative_time_delta, default_start_date, utc) 
            for i, (home_id, last_updated, device_map) in enumerate(home_data)]

    # Use multiprocessing pool with starmap
    with mp.Pool(processes=MAX_PROCESSES) as pool:
        pool.starmap(process_building, args)

    logger.info("All buildings processed.")

if __name__ == '__main__':
    run_pipeline()
