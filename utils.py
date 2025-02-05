import os
from datetime import datetime
from config import *

def getTimestamp():
    now = datetime.now()
    return datetime.strftime(now, "%m%d%Y%H%M%S")

def getCurrentime():
    return datetime.now()

def getFileModifiedDate(filepath):
    return datetime.fromtimestamp(os.path.getmtime(filepath))

def getDaysDifferent(currentTime, timestamp):
    return (currentTime - timestamp).days

def cubicInchesToCubicFeet(l, w, h):
    return round((l * w * h) / 1728, 3)

def getBoxMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, BOX_MASTER_FILENAME)

def getInventoryMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, INVENTORY_MASTER_FILENAME)

def volumeIsBiggerByAtLeast(percentThreshold, biggerVolume, smallerVolume):
    biggerPercentage = (abs(biggerVolume - smallerVolume) / smallerVolume) * 100
    return biggerPercentage > percentThreshold
