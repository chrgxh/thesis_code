import json
from datetime import datetime
from typing import List
from device_and_building import Device,Building
from common import *

def yield_home_map_and_last_updated():
    """
    Yields (home_id, last_updated, device_map) for each home in the given JSON config file.
    
    device_map is a dict of {device_id: index}, where:
      - The first meter device (is_meter == True) is always assigned index 0.
      - All other devices follow in their original order, with sequential indexes 1,2,...
    """
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for home in data:
        # Skip if active_in_pipeline is false
        if not home.get("active_in_pipeline", False):
            continue

        last_updated = home["last_updated"]
        home_id = home["home_id"]
        devices = home.get("devices", [])

        # Identify the first meter device
        meter_device = None
        for d in devices:
            if d.get("is_meter") is True:
                meter_device = d
                break

        device_map = {}
        next_index = 1

        # If we found a meter, assign it index 0
        if meter_device:
            device_map[meter_device["device_meter_id"]] = 0

        # Now assign indexes to all other devices in order
        for d in devices:
            if d is meter_device:
                continue  # already assigned index=0
            if not d.get("active_in_pipeline", False):
                continue  # not active device
            device_map[d["device_meter_id"]] = next_index
            next_index += 1

        # Yield a tuple of (home_id,last_updated, device_map)
        yield home_id,last_updated, device_map


def load_buildings_from_json(json_path: str) -> List[Building]:
    """
    Reads the JSON configuration file at json_path and returns a list of Building objects.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    buildings = []
    for home_entry in data:
        # home_entry is a dict with keys like home_id, last_updated, active_in_pipeline, devices
        if home_entry["active_in_pipeline"]:
            home_id = str(home_entry["home_id"])  # cast to str if you want consistency with Building's __init__

            device_list = []
            for device_data in home_entry["devices"]:
                # Construct a dict compatible with Device.from_dict
                if device_data["active_in_pipeline"]:
                    dev_dict = {
                        "home_id": home_id,
                        "device_id": device_data["device_meter_id"],
                        # device_type_text is used by is_meter() in the Device class
                        "device_type_text": device_data["device_type"],      # e.g. "3-phase EM" or "Shelly Plug S"
                        "device_name": device_data["appliance_name"],        # e.g. "television", "air conditioner", or ""
                        "device_type": device_data["type"],                  # e.g. "TV", "AC", "meter", etc.
                    }

                    # Create a Device instance using your from_dict factory method
                    device_obj = Device.from_dict(dev_dict)
                    device_list.append(device_obj)

            # Create a Building with its associated device list
            building = Building(home_id=home_id, device_list=device_list)
            buildings.append(building)

    return sorted(buildings,key=lambda building: int(building.home_id))

def update_building_last_updated(home_id: int, last_updated_value: str):
    """
    Updates the 'last_updated' field of the building (home) with the specified home_id
    in the provided JSON file. If not found, the function does nothing.

    :param json_file_path: Path to the JSON config file.
    :param home_id: The integer home_id of the building to update.
    :param last_updated_value: The datetime string to set in 'last_updated'.
    """
    # 1. Read the JSON data
    with open(JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    # 2. Iterate through the list of homes
    for home in data:
        if home.get("home_id") == home_id:
            # 3. Update last_updated with the provided value
            home["last_updated"] = last_updated_value
            break  # Stop after updating the matching home

    # 4. Write updated data back to the file
    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def reset_last_updated_in_config(json_file_path: str):
    """
    Loads the JSON config file at json_file_path, sets every 'last_updated'
    field to an empty string, and overwrites the file with these changes.
    """
    with open(json_file_path, "r") as file:
        data = json.load(file)

    for home_entry in data:
        home_entry["last_updated"] = ""

    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=2)

if __name__ == '__main__':
    reset_last_updated_in_config(JSON_PATH)