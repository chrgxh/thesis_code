from typing import List
import re
from collections import OrderedDict
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

# Initialize ruamel.yaml instance
yaml = YAML()
yaml.default_flow_style = False

# Define reusable objects with explicit anchors
clamp = CommentedMap({"site_meter": True, "device_model": "Clamp"})
iam = CommentedMap({"submeter_of": 0, "device_model": "IAM"})

# Assign custom anchor names
clamp.yaml_set_anchor("clamp")
iam.yaml_set_anchor("iam")

class Device:
    def __init__(self, home_id, device_id: str, device_type_text: str, device_name: str, device_type: str):
        self.home_id = home_id
        self.device_id = device_id
        self.device_type_text = device_type_text
        self.device_name = device_name
        self.device_type = device_type
        self.clamp = clamp
        self.iam = iam

    def get_device_type(self):
        return re.sub(r'[\d-]', '', self.device_type)
    
    def is_meter(self):
        return 'phase' in self.device_type_text.lower()

    def get_meter_device(self):
        if self.is_meter():
            return self.clamp
        else:
            return self.iam

    @classmethod
    def from_dict(cls, device_dict: dict):
        """Alternative constructor to create a Device instance from a dictionary."""
        return cls(
            home_id=device_dict["home_id"],
            device_id=device_dict["device_id"],
            device_type_text=device_dict["device_type_text"],
            device_name=device_dict["device_name"],
            device_type=device_dict["device_type"]
        )

class Building:
    def __init__(self, home_id: str, device_list: List[Device]):
        self.home_id = home_id
        self.device_list = device_list

    def __str__(self):
        device_count = len(self.device_list)
        return f"Building(home_id={self.home_id}, device_count={device_count})"

    def __repr__(self):
        return self.__str__()
    
    def generate_building_yaml(self, building_no: int, file_path: str):
        # Map devices to elec_meters and appliances
        elec_meters = CommentedMap()
        appliances = []

        for index, device in enumerate(self.device_list, start=1):
            elec_meters[index] = device.get_meter_device()
            if not device.is_meter():
                # Add to appliances
                appliances.append({
                    "original_name": device.get_device_type().lower(),
                    "type": device.get_device_type().lower(),
                    "instance": 1,  # Default instance for simplicity
                    "meters": [index],
                })
    
        # Construct final YAML structure
        yaml_data = CommentedMap([
            ("instance", building_no),
            ("original_name", f"House{self.home_id}"),
            ("elec_meters", elec_meters),
            ("appliances", appliances),
        ])
        
        for appliance in yaml_data["appliances"]:
            appliance["meters"] = yaml.seq(appliance["meters"])
            appliance["meters"].fa.set_flow_style()

        # Write the YAML file
        with open(file_path, "w") as yaml_file:
            yaml.dump(yaml_data, yaml_file)

