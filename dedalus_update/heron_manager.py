from heron_utils.query_heron import _get_device_measurement, _init_heron_api
from heron_utils.settings import HISTORY
from logger_config import logger
from datetime import datetime, timezone
from typing import List, Tuple

heron_api = _init_heron_api()

TIME_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"

def get_nano_time_from_time_string(time:str)->str:
    time = datetime.strptime(time, TIME_FORMAT)
    time_ns = int(time.timestamp() * 1e9)
    return time_ns

def get_heron_device_data(device_id: str, start_time: str, end_time: str) -> dict:
    try:
        resp_dict = _get_device_measurement(
            heron_api_instance=heron_api,
            device_id=device_id,
            time_from_nano=start_time,
            time_to_nano=end_time
        )

        if not resp_dict:
            logger.warning("API returned None (no response)")
            return None

        if "power" in resp_dict:
            power=resp_dict.get("power")
            if power:
                return power
            else:
                logger.warning(f"No power found for {device_id} between {start_time} and {end_time}")
                return None

        if "error" in resp_dict:
            logger.warning(f"API error: {resp_dict['error']}")
            return None

        logger.warning("No power or error key in response.")
        return None

    except Exception as e:
        logger.error(f"Unexpected failure in get_heron_device_data: {str(e)}")
        raise e


def get_device_info() -> List[Tuple[str, datetime]]:
    return [
        (device["deviceid"], datetime.strptime(device["registeredat"], TIME_FORMAT).replace(tzinfo=timezone.utc))
        for device in HISTORY
    ]
