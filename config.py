from pathlib import Path

APP_VERSION = '1.0.1'

ASSETS_BASE_DIR = 'S:/ECOM-CC-WHS/master_files'
UOM_MASTER_FILENAME = 'uom_input.csv'
INVENTORY_MASTER_FILENAME = 'Available Qty Whse 01 + 05.xlsx'
LOGS_FILENAME = 'logs.txt'
USER_DOWNLOADS = str(Path.home() / "Downloads") + '/'
OUTPUT_DIR = './batch_outputs/'

MAX_WEIGHT_PER_BOX = 40 # 40 lbs
BOX_DIMENSION_PADDING = 0.5 # 0.5 inch