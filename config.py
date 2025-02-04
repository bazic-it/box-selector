from pathlib import Path
import json

def readConfigJson():
    configs = {
        "app_configs": {
            "assets_base_directory": "",
            "boxes_master_filepath": "",
            "inventory_master_filepath": "",
            "input_file_location": ""
        },
        "packing_configs":{
            "max_weight_per_box": 0,
            "box_dimension_padding": 0,
            "ship_case_as_is_weight_threshold": 0,
            "volume_bigger_by_threshold": 0
        }
    }

    jsonFilepath = "./assets/config.json"

    with open(jsonFilepath, 'r') as file:
        data = json.load(file)
        if data:
            configs = data

    return configs

configs = readConfigJson()

APP_VERSION = '1.0.8'

# ASSETS_BASE_DIR = 'S:/!Warehouse/Box Selector Master'
ASSETS_BASE_DIR = configs["app_configs"]["assets_base_directory"]
BOX_MASTER_FILENAME = configs["app_configs"]["boxes_master_filepath"]
INVENTORY_MASTER_FILENAME = configs["app_configs"]["inventory_master_filepath"]
# LOGS_FILENAME = 'logs.txt'
USER_DOWNLOADS = str(Path.home() / configs["app_configs"]["input_file_location"]) + '/'
# OUTPUT_DIR = './batch_outputs/'

MAX_WEIGHT_PER_BOX = configs["packing_configs"]["max_weight_per_box"]
BOX_DIMENSION_PADDING = configs["packing_configs"]["box_dimension_padding"]
SHIP_CASE_AS_IS_WEIGHT_THRESHOLD = configs["packing_configs"]["ship_case_as_is_weight_threshold"]
VOLUME_BIGGER_BY_THRESHOLD = configs["packing_configs"]["volume_bigger_by_threshold"]