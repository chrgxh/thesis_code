from datetime import datetime, timedelta
import json
import time
import psycopg2
from heron_utils.settings import HISTORY
from heron_utils.heron_api import HeronApi

# DEDALUS POSTGRES SETTINGS
DEDALUS_PG = {
    'HOSTNAME': "dedalus_postgres",
    #'HOSTNAME': "dedalus.epu.ntua.gr",
    'PORT': 5432,
    'USER': "dedalus",
    'PASSWORD': "dedalus",
    'DB': "dedalus"
}

CHUNK_SIZE_DAYS = 31

def _init_heron_api():
    heron_api_instance = HeronApi()
    return heron_api_instance

def _get_token(heron_api_instance):
    token = heron_api_instance._get_token()
    return token

def _get_device_measurement(heron_api_instance, device_id, time_from_nano, time_to_nano):
    device_response = heron_api_instance._device_data(
        device_id=device_id,
        time_from=time_from_nano,
        time_to=time_to_nano,
        measurement='power'  # Fetch only 'power' measurements
    )
    return device_response

def create_table():
    try:
        connection = psycopg2.connect(
            dbname=DEDALUS_PG['DB'],
            user=DEDALUS_PG['USER'],
            password=DEDALUS_PG['PASSWORD'],
            host=DEDALUS_PG['HOSTNAME'],
            port=DEDALUS_PG['PORT']
        )
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_measurements_30 (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(255),       
                timestamp TIMESTAMP WITH TIME ZONE,
                power_data FLOAT,
                phase INTEGER
            )
        """)

        connection.commit()
        print("Table 'device_measurements_30' created successfully")

    except psycopg2.Error as e:
        print("Error while creating table:", e)

    finally:
        cursor.close()
        connection.close()

def _save_to_postgres(data):
    create_table()  # Call create_table before inserting data
    try:
        connection = psycopg2.connect(
            dbname=DEDALUS_PG['DB'],
            user=DEDALUS_PG['USER'],
            password=DEDALUS_PG['PASSWORD'],
            host=DEDALUS_PG['HOSTNAME'],
            port=DEDALUS_PG['PORT']
        )

        cursor = connection.cursor()

        for device_id, power_data in data.items():
            for phase, measurements in power_data.items():
                for entry in measurements:
                    if isinstance(entry, dict):
                        timestamp_str = entry.get("time")
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                        power_value = entry.get("value")

                        if timestamp is not None and power_value is not None:
                            # Check if the record already exists
                            cursor.execute(
                                "SELECT COUNT(*) FROM device_measurements_30 WHERE device_id = %s AND timestamp = %s AND phase = %s",
                                (device_id, timestamp, int(phase))
                            )
                            count = cursor.fetchone()[0]

                            if count == 0:  # If no such record exists, insert the new data
                                cursor.execute(
                                    "INSERT INTO device_measurements_30 (device_id, timestamp, power_data, phase) VALUES (%s, %s, %s, %s)",
                                    (device_id, timestamp, power_value, int(phase))
                                )

        connection.commit()
        print("Data successfully saved to PostgreSQL")

    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL:", e)

    finally:
        try:
            cursor.close()
        except NameError:
            pass
        try:
            connection.close()
        except NameError:
            pass

def heron_device_history(device_id_to_fetch):
    list_of_devices = HISTORY
    heron_api_instance = _init_heron_api()
    result_data = {}

    for device in list_of_devices:
        if device['deviceid'] != device_id_to_fetch:
            continue  # Skip devices not matching the specified device_id

        device_id = device['deviceid']
        device_start_time = datetime.strptime(device['registeredat'], "%Y-%m-%dT%H:%M:%S.%fZ")

        # Initialize result data for the device if not present
        if device_id not in result_data:
            result_data[device_id] = {}

        current_time = datetime.now()

        while device_start_time < current_time:
            # Calculate the end time for the current chunk
            device_end_time = min(device_start_time + timedelta(days=CHUNK_SIZE_DAYS), current_time)

            # Convert to nano timestamps
            device_start_time_nano = int(device_start_time.timestamp() * 1000000000)
            device_end_time_nano = int(device_end_time.timestamp() * 1000000000)
            print('start ', device_start_time_nano, ' end ', device_end_time_nano)

            # Get device data for the current chunk
            device_data = _get_device_measurement(
                heron_api_instance,
                device_id,
                device_start_time_nano,
                device_end_time_nano,
            )

            # Check if device_data is not None before updating result_data
            if device_data is not None and 'power' in device_data:
                # Update the result data for the device
                result_data[device_id].update(device_data['power'])
            else:
                print(f"No power measurements data found for device {device_id}")

            # Move to the next chunk
            device_start_time = device_end_time

            # Save data to PostgreSQL for this chunk
            # _save_to_postgres({device_id: result_data[device_id]})

            # Small delay to prevent overwhelming the server with requests
            time.sleep(1)

    return result_data

if __name__ == '__main__':
    device_id_to_fetch = input("Enter the device ID to fetch: ")  # Device ID to fetch
    result = heron_device_history(device_id_to_fetch)
