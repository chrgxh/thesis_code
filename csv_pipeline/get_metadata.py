from query_db_access_api import query_db_access_api
from device_and_building import Device, Building
from typing import List
import os
from buildings_json_handler import load_buildings_from_json
from common import *

#probably not necessary, is not used
def extract_house_list()->List[Building]:
    """
    Gets a list of buildings by querying the database.
    """
    query = """
    SELECT home_id, 
        device_id, 
        device_type_text, 
        device_name, 
        device_type
    FROM device_metadata
    ORDER BY home_id, device_id;
    """
    query_payload = {
    "query": query
    }

    device_list=query_db_access_api(query_payload).to_dict(orient="records")
    #device_list is ordered by home_id and device_id
    
    building_list:List[Building]=[]
    for device in device_list:
        my_device=Device.from_dict(device)
        building = next((building for building in building_list if building.home_id == my_device.home_id), None)
        if building:
            building.device_list.append(my_device)
        else:
            building_list.append(Building(my_device.home_id,[my_device]))
    
    return sorted(building_list,key=lambda building: int(building.home_id))

def get_device_metadata():
    """
    Generate YAML metadata for each building in the list and save to files.
    """
    building_list = load_buildings_from_json(JSON_PATH)

    for index, building in enumerate(building_list, start=1):
        output_file = os.path.join(METADATA_DIR, f'building{index}.yaml')
        building.generate_building_yaml(index, output_file)

if __name__ == '__main__':
    #print(extract_house_list())
    get_device_metadata()