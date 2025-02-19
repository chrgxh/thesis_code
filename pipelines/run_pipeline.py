import pandas as pd
import pytz
import os
from loguru import logger
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from query_db_access_api import query_db_access_api
from transformations import *
from common import *
from buildings_json_handler import yield_home_map_and_last_updated, update_building_last_updated

# Example SQL query to test the database connection
query_payload = {
    "query": "SELECT * FROM your_table LIMIT 5;"  # Replace 'your_table' with an actual table name
}

def get_data_for_device_in_period(devices:str,start_date:datetime,end_date:datetime)->pd.DataFrame:

    start_str = start_date.isoformat()   
    end_str   = end_date.isoformat()

    query = f"""
        SELECT device_id , timestamp , power_data , phase
        FROM device_measurements_30
        WHERE device_id IN ({devices})
          AND "timestamp" >= '{start_str}'
          AND "timestamp" < '{end_str}'
        ORDER BY "timestamp" ASC;
    """
    query_payload['query']=query
    return query_db_access_api(query_payload)

def run_pipeline():
    utc = pytz.UTC
    default_start_date = datetime(2021, 1, 1 , 0 , 0 , 0 , tzinfo=utc)
    relative_time_delta=relativedelta(months=1)
    
    count=1
    for home_id, last_updated, device_map in yield_home_map_and_last_updated():

        if count>1:
            break

        logger.info(f"Retrieving data batch with the following details.")
        logger.info(f"Home id: {home_id}")
        logger.info(f"Last updated: {last_updated}")
        logger.info(f"Device map: {device_map}")
        logger.info("---")

        devices_str=",".join(f"'{key}'" for key in device_map.keys())

        #start time is set 1 second after last updated if last updated exists in the json file
        start_date=datetime.fromisoformat(last_updated)+timedelta(seconds=1) if last_updated else default_start_date
        while start_date <= datetime.now(utc):

            end_date=start_date+relative_time_delta

            df=get_data_for_device_in_period(devices_str,start_date, end_date)

            if df.empty:
                logger.warning("No data found.")
                start_date=end_date
                continue

            df=apply_transformations(
                df,
                remove_milliseconds,
                (map_device_id,device_map),
                aggregate_power,
                (reshape_power_data,len(device_map.keys()))
            )
            
            file_path=fr'{DATA_DIR}\combined_main_and_meters_{count}.csv'
            df.to_csv(
                file_path, 
                mode='a',  # Append mode
                index=False, 
                header=not os.path.exists(file_path)  # Write header only if file does not already exist
            )

            start_date=end_date
            updated_at:datetime=df.iloc[-1]['timestamp'].to_pydatetime()
            update_building_last_updated(home_id,updated_at.isoformat())
            logger.info("Batch processing completed.")
        count+=1

if __name__ == '__main__':
    run_pipeline()