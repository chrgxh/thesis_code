import yaml
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple

last_update_file_path="pipeline_config.yaml"

def update_last_updated(path=last_update_file_path, new_dt=None):
    if new_dt is None:
        new_dt = datetime.utcnow()

    new_ts = new_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    with open(path) as f:
        config = yaml.safe_load(f)

    config["last_updated"] = new_ts

    with open(path, "w") as f:
        yaml.safe_dump(config, f)



def read_last_updated(config_path="pipeline_config.yaml"):
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return datetime.strptime(config["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
    except (FileNotFoundError, KeyError, ValueError):
        return datetime(2021, 6, 20)

def read_config_values(config_path: str = "pipeline_config.yaml") -> Tuple[datetime, int, relativedelta]:
    """
    Reads the pipeline configuration from a YAML file and returns:
    - last_updated: datetime in UTC
    - num_processes: number of worker processes to use
    - relative_delta: time delta as a relativedelta object (in days)

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        Tuple[datetime, int, relativedelta]: Parsed config values.
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    last_updated: datetime = datetime.strptime(config["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
    num_processes: int = int(config["num_processes"])
    relative_delta: relativedelta = relativedelta(days=int(config["relative_delta"]))

    return last_updated, num_processes, relative_delta

