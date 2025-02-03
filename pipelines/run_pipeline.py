import pandas as pd
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from house_list_extractor import extract_house_list
from query_db_access_api import QUERY_ENDPOINT, query_db_access_api
from transformations import *

# Example SQL query to test the database connection
query_payload = {
    "query": "SELECT * FROM your_table LIMIT 5;"  # Replace 'your_table' with an actual table name
}

data_dir=r'D:\thesis_code\my_code\pipelines\data'

def get_monthly_data_for_device(devices:str,start_date:datetime)->pd.DataFrame:
    end_date = start_date + relativedelta(months=1)

    year  = start_date.year
    month = start_date.month

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

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
    return query_db_access_api(QUERY_ENDPOINT,query_payload)

def run_pipeline(data_dir:str,start_date:datetime=None):
    # building_list = extract_house_list()
    # for index, building in enumerate(building_list, start=1):
    #     for device in building.device_list:
    #         query_payload = {
    #         "query": "SELECT * FROM device_metadata LIMIT 5;" 
    #         }
    #         df=query_db_access_api(QUERY_ENDPOINT,query_payload)
    #         print(df.head())
    #         print(df.columns.tolist())
    utc = pytz.UTC
    start_date_example = datetime(2023, 10, 10 , 0 , 0 , 0 , tzinfo=utc)
    # building_devices=building_list[0].get_device_list_as_string()
    # df=get_monthly_data_for_device(building_list[0].device_list[0].device_id,start_date_example)
    df=get_monthly_data_for_device("'domxem3-ECFABCC7F0FF','shellyplug-s-F1C2FB'",start_date_example)
    device_mappings={'domxem3-ECFABCC7F0FF':0,'shellyplug-s-F1C2FB':1}
    df=apply_transformations(
        df,
        remove_milliseconds,
        (map_device_id,device_mappings),
        aggregate_power,
        (reshape_power_data,len(device_mappings.keys()))
    )
    print(df.head(10))
    print(df.columns)

if __name__ == '__main__':
    run_pipeline(data_dir)