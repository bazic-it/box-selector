from pathlib import Path

APP_VERSION = '1.0.6'

# ASSETS_BASE_DIR = 'S:/!Warehouse/Box Selector Master'
ASSETS_BASE_DIR = './'
BOX_MASTER_FILENAME = 'boxes_master.csv'
INVENTORY_MASTER_FILENAME = 'Item List with PICTURE (For Excel) - All Items.xlsx'
# LOGS_FILENAME = 'logs.txt'
USER_DOWNLOADS = str(Path.home() / "Downloads") + '/'
# OUTPUT_DIR = './batch_outputs/'

MAX_WEIGHT_PER_BOX = 40 # 40 lbs
BOX_DIMENSION_PADDING = 0.5 # 0.5 inch
SHIP_CASE_AS_IS_WEIGHT_THRESHOLD = 20 # 20 lbs
VOLUME_BIGGER_BY_THRESHOLD = 50 # 50%