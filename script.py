import os
import csv
import pandas as pd
import openpyxl
from functools import cmp_to_key
from utils import *
from config import *


dummyBoxes = [
    {
        'name': 'A',
        'length': 12.0,
        'width': 11.5,
        'height': 9.5,
        'volume': 0.759
    },
    {
        'name': 'B',
        'length': 20.0,
        'width': 15.5,
        'height': 12.5,
        'volume': 2.242
    },
    {
        'name': 'C',
        'length': 25.5,
        'width': 18.2,
        'height': 16.5,
        'volume': 4.431
    }
]

class ItemLine:
    def __init__(self):
        self.sku = None
        self.itemDescription = None
        self.uomCode = None
        self.qty = None
        self.pricePerPiece = None
        self.totalLC = None
        self.unitPrice = None
        self.available = None
        self.length = None
        self.width = None
        self.height = None
        self.volume = None
        self.weight = None

    def __str__(self):
        return 'sku: {}, UOM Code: {}, qty: {}, dimension: {} x {} x {}, volume: {}, weight: {}'.format(self.sku, self.uomCode, self.qty, self.length, self.width, self.height, self.volume, self.weight)

def sortOrders(a, b):
    if a[2] == 'CASE' and (b[2] == 'BOX' or b[2] == 'EA'):
        return -1
    elif a[2] == 'BOX' and b[2] == 'EA':
        return -1
    else:
        return 1

def getInventoryMasterData(inputFilepath):
    age = getDaysDifferent(getCurrentime(), getFileModifiedDate(inputFilepath))
    message = 'Inventory master file was updated {} days ago.'.format(age)

    targetColumns = ['Item No.', 'Available Qty', 'Case Length', 'Case Width', 'Case Height', 'Case Volume', 'Case Weight', 'Box Length', 'Box Width', 'Box Height', 'Box Volume', 'Box Weight', 'EA Length', 'EA Width', 'EA Height', 'EA Volume', 'EA Weight']
    keyColumn = 'Item No.'
    headerMap = {}
    mapped = {}

    try:
        workbook = openpyxl.load_workbook(inputFilepath)
        sheet = workbook.active
        for r in range(1, sheet.max_row+1):
            itemNumber = None
            for c in range(1, sheet.max_column+1):
                data = sheet.cell(row=r, column=c).value
                if r == 1:
                    for colName in targetColumns:
                        if data == colName:
                            headerMap[c] = colName
                else:
                    if c in headerMap:
                        if headerMap[c] == keyColumn:
                            itemNumber = str(data)
                            mapped[itemNumber] = {}
                        else:
                            mapped[itemNumber][headerMap[c]] = data
    except Exception as e:
        print('*** Error: Failed to read input file for Inventory Master: {} ***'.format(e))
        return {}, message
  
    return mapped, message

def getSalesQuotationItemsFromInputfile(filepath):
    age = getDaysDifferent(getCurrentime(), getFileModifiedDate(filepath))
    message = 'Inventory master file was updated {} days ago.'.format(age)

    targetColumns = ['Item No.', 'Item Description', 'UoM Code', 'Quantity', 'Price Per Piece', 'Total (LC)', 'Unit Price', 'Available Qty']
    headerMap = {}
    items = []
    
    try:
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active
        for r in range(1, sheet.max_row+1):
            item = {}
            itemNumber = None
            for c in range(1, sheet.max_column+1):
                data = sheet.cell(row=r, column=c).value
                if r == 1:
                    for colName in targetColumns:
                        if data == colName:
                            headerMap[c] = colName
                else:
                    if c in headerMap:
                        item[headerMap[c]] = data
            if item:
                items.append(item)

    except Exception as e:
        print('*** Error: Failed to read input file for Sales Quotation: {} ***'.format(e))
        return {}, message
    
    return items, message

def convertStringToFloat(value):
    if type(value) == str:
        value = value.replace('$', '')
        return float(value)
    return float(value)

def combineDetailsForEachItem(inventoryMaster, items):
    itemLines = []
    itemsWithNoInfo = []

    for i in items:
        if not i['Item No.']:
            continue
        sku = i['Item No.']
        if sku in inventoryMaster:
            item = ItemLine()
            item.sku = sku
            item.itemDescription = i['Item Description']
            item.qty = int(i['Quantity'])
            item.pricePerPiece = convertStringToFloat(i['Price Per Piece'])
            item.totalLC = convertStringToFloat(i['Total (LC)'])
            item.unitPrice = convertStringToFloat(i['Unit Price'])
            item.available = int(i['Available Qty'])

            uomCode = i['UoM Code']
            if uomCode:
                item.uomCode = uomCode
                if uomCode == 'EA':
                    item.length = float(inventoryMaster[sku]['EA Length']) if 'EA Length' in inventoryMaster[sku] else None
                    item.width = float(inventoryMaster[sku]['EA Width']) if 'EA Width' in inventoryMaster[sku] else None
                    item.height = float(inventoryMaster[sku]['EA Height']) if 'EA Height' in inventoryMaster[sku] else None
                    item.volume = float(inventoryMaster[sku]['EA Volume']) if 'EA Volume' in inventoryMaster[sku] else None
                    item.weight = float(inventoryMaster[sku]['EA Weight']) if 'EA Weight' in inventoryMaster[sku] else None
                elif uomCode == 'BOX':
                    item.length = float(inventoryMaster[sku]['Box Length']) if 'Box Length' in inventoryMaster[sku] else None
                    item.width = float(inventoryMaster[sku]['Box Width']) if 'Box Width' in inventoryMaster[sku] else None
                    item.height = float(inventoryMaster[sku]['Box Height']) if 'Box Height' in inventoryMaster[sku] else None
                    item.volume = float(inventoryMaster[sku]['Box Volume']) if 'Box Volume' in inventoryMaster[sku] else None
                    item.weight = float(inventoryMaster[sku]['Box Weight']) if 'Box Weight' in inventoryMaster[sku] else None
                elif uomCode == 'CASE':
                    item.length = float(inventoryMaster[sku]['Case Length']) if 'Case Length' in inventoryMaster[sku] else None
                    item.width = float(inventoryMaster[sku]['Case Width']) if 'Case Width' in inventoryMaster[sku] else None
                    item.height = float(inventoryMaster[sku]['Case Height']) if 'Case Height' in inventoryMaster[sku] else None
                    item.volume = float(inventoryMaster[sku]['Case Volume']) if 'Case Volume' in inventoryMaster[sku] else None
                    item.weight = float(inventoryMaster[sku]['Case Weight']) if 'Case Weight' in inventoryMaster[sku] else None
                else:
                    item.length = None
                    item.width = None
                    item.height = None
                    item.volume = None
                    item.weight = None
            itemLines.append(item)
        else:
            itemsWithNoInfo.append(sku)
    
    return itemLines, itemsWithNoInfo

def distributeToBoxes(boxes, itemLines):
    activeBoxes = [[boxes[i]['volume'], 0] for i in range(len(boxes))]
    activeBoxesContent = [[] for i in range(len(boxes))]

    boxIndex = 0
    for item in itemLines:
        while (activeBoxes[boxIndex][0] < item.volume or (activeBoxes[boxIndex][1] + item.weight) > MAX_WEIGHT_PER_BOX) and boxIndex < len(activeBoxes):
            boxIndex += 1
        if activeBoxes[boxIndex][0] >= item.volume and (activeBoxes[boxIndex][1] + item.weight) <= MAX_WEIGHT_PER_BOX:
            activeBoxes[boxIndex][0] -= item.volume
            activeBoxes[boxIndex][1] += item.weight
            activeBoxesContent[boxIndex].append(item)
        boxIndex = 0

    return activeBoxes, activeBoxesContent

def compileResults(boxesMaster, boxes, boxesContents):
    results = {}

    for i in range(len(boxes)):
        if boxesContents[i]:
            results[boxesMaster[i]['name']] = {
                'volumeFilled': round(boxesMaster[i]['volume'] - boxes[i][0], 3),
                'weight': round(boxes[i][1], 3),
                'contents': boxesContents[i],
                'length': boxesMaster[i]['length'],
                'width': boxesMaster[i]['width'],
                'height': boxesMaster[i]['height']
            }

    return results

def displayResultsAsString(results):
    texts = []
    count = 1
    for boxName, info in results.items():
        contents = []
        for item in info['contents']:
            contents.append('{}-{:<8}x{}'.format(item.sku, item.uomCode, item.qty))

        texts.append('{}. Box - {} ({}"x{}"x{}")'.format(count, boxName, info['length'], info['width'], info['height']))
        texts.append('Weight: {} Lb'.format(info['weight']))
        texts.append('Contents:\n{}'.format('\n'.join(contents)))
        texts.append(' ')
        count += 1

    return texts

def distribute(filepath):
    success = True

    inventoryMaster, invMsg = getInventoryMasterData('./warehouse_master.xlsx')
    items, itemsMsg = getSalesQuotationItemsFromInputfile("./sq_2.xlsx")
    itemLines, itemsWithNoInfo = combineDetailsForEachItem(inventoryMaster, items)

    boxes, boxesContents = distributeToBoxes(dummyBoxes, itemLines)

    results = compileResults(dummyBoxes, boxes, boxesContents)

    return {
        'success': True,
        'results': displayResultsAsString(results)
    }

def validateInputFilename(filename):
    cleaned = filename
    if '/' in filename:
        cleaned = filename.split('/')[-1]

    if '.xlsx' not in cleaned:
        cleaned = cleaned + '.xlsx'

    return USER_DOWNLOADS + cleaned

def getUOMMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, UOM_MASTER_FILENAME)

def getInventoryMasterFilepath():
    return os.path.join(ASSETS_BASE_DIR, INVENTORY_MASTER_FILENAME)

def writeLog(timestamp, status):
    path = os.path.join(ASSETS_BASE_DIR, LOGS_FILENAME)
    user = os.getenv('COMPUTERNAME')
    try:
        with open(path, 'a') as file:
            file.write('USR;{} | IN;{} | SUCCESS;{} | ERR;{} | WARNING;{} | WARN;{} | OOS;{} | OUT;{} | VER;{} | TS;{}\n'.format(user, status["inputFilename"], status["success"], status["errorMessage"], status["warning"], status["warningMessage"], status["outOfStockSKUs"], status["outputFilename"], APP_VERSION, timestamp))
    except:
        print('*** Error: Failed to write to logs. ***')