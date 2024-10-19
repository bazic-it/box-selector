import os
import csv
import pandas as pd
import openpyxl
from functools import cmp_to_key
from utils import *
from config import *

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

def sortBoxes(boxes):
    return sorted(boxes, key=lambda b:b['volume'])

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

def getBoxesMasterData(inputFilepath):
    boxes = []
    message = None

    try:
        age = getDaysDifferent(getCurrentime(), getFileModifiedDate(inputFilepath))
        message = 'Boxes master file was updated {} days ago.'.format(age)
        row = 0
        with open (inputFilepath, mode='r') as file:
            content = csv.reader(file)
            for line in content:
                if row == 0:
                    row += 1
                    continue
                length = float(line[1])
                width = float(line[2])
                height = float(line[3])
                weight = float(line[4])
                volume = cubicInchesToCubicFeet(length, width, height)
                boxes.append({
                        'name': line[0],
                        'length': length,
                        'width': width,
                        'height': height,
                        'volume': volume,
                        'weight': weight
                    })
                row += 1
    except:
        print('*** Error: Failed to read input file for UOM Master. Please make sure filename is valid. ***')
        return {}, message

    return boxes, message

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

def splitCasesAndBoxesForEachItem(itemLines):
    newItemLines = []

    for item in itemLines:
        if item.uomCode == 'CASE' and item.qty > 1:
            itemQty = item.qty
            item.qty = 1
            newItemLines.append(item)
            for _ in range(itemQty - 1):
                newItem = ItemLine()
                newItem.sku = item.sku
                newItem.itemDescription = item.itemDescription
                newItem.uomCode = item.uomCode
                newItem.qty = 1
                newItem.pricePerPiece = item.pricePerPiece
                newItem.totalLC = item.totalLC
                newItem.unitPrice = item.unitPrice
                newItem.available = item.available
                newItem.length = item.length
                newItem.width = item.width
                newItem.height = item.height
                newItem.volume = item.volume
                newItem.weight = item.weight
                newItemLines.append(item)
        else:
            newItemLines.append(item)

    return newItemLines

def distributeToBoxes(boxes, itemLines):
    # Sort items from highest volume to lowest volume
    itemLines.sort(key=lambda i:i.volume, reverse=True)
    # Sort boxes from lowest volume to highest volume
    boxes = sortBoxes(boxes)

    activeBoxes = []
    activeBoxesContent = []
    itemsDoNotFit = []

    for item in itemLines:
        foundABox = False
        itemTotalVolume = item.volume * item.qty
        itemTotalWeight = item.weight * item.qty
        # look at previous boxes
        if activeBoxes:
            for i in range(len(activeBoxes)):
                # if item fits in a previous box
                if activeBoxes[i][0] >= itemTotalVolume and activeBoxes[i][1] + itemTotalWeight <= MAX_WEIGHT_PER_BOX:
                    activeBoxes[i][0] -= itemTotalVolume
                    activeBoxes[i][1] += itemTotalWeight
                    activeBoxesContent[i].append(item)
                    # activeBoxesContent[i].append('{}-{}'.format(item.sku, item.uomCode)) # for debugging
                    foundABox = True
                    break
                # check if we can combine item(s) from previous box with current item in a bigger box
                nextBoxIndex = activeBoxes[i][4] + 1
                if activeBoxes[i][0] != -1 and nextBoxIndex >= 0 and nextBoxIndex < len(boxes):
                    nextBox = boxes[nextBoxIndex]
                    currentBoxTotalVolume = activeBoxes[i][0]
                    currentBoxTotalWeight = activeBoxes[i][1]
                    currentBoxWeight = activeBoxes[i][2]
                    newBoxWeight = nextBox['weight'] - currentBoxWeight
                    if currentBoxTotalVolume + itemTotalVolume <= nextBox['volume'] and currentBoxTotalWeight + itemTotalWeight + newBoxWeight <= MAX_WEIGHT_PER_BOX:
                        activeBoxes.append([nextBox['volume'] - (currentBoxTotalVolume + itemTotalVolume), currentBoxTotalWeight + itemTotalWeight + newBoxWeight, nextBox['weight'], nextBox['name'], nextBoxIndex])
                        activeBoxesContent.append([item] + activeBoxesContent[i])
                        # activeBoxesContent.append(['{}-{}'.format(item.sku, item.uomCode)] + activeBoxesContent
                        #                              [i]) # for debugging
                        activeBoxes[i][0] = -1
                        activeBoxesContent[i] = []
                        foundABox = True
                        break
        # find a new box
        if not foundABox:
            for i in range(len(boxes)):
                if itemTotalVolume <= boxes[i]['volume'] and itemTotalWeight + boxes[i]['weight'] <= MAX_WEIGHT_PER_BOX:
                    activeBoxes.append([boxes[i]['volume'] - itemTotalVolume, itemTotalWeight + boxes[i]['weight'], boxes[i]['weight'], boxes[i]['name'], i])
                    activeBoxesContent.append([item])
                    # activeBoxesContent.append(['{}-{}'.format(item.sku, item.uomCode)]) # for debugging
                    foundABox = True
                    break
        # item could not find a box
        if not foundABox:
            itemsDoNotFit.append(item.sku)

    return activeBoxes, activeBoxesContent, itemsDoNotFit

def compileResults(boxesMaster, boxes, boxesContents):
    results = []
    boxesMap = {}

    for box in boxesMaster:
        boxesMap[box['name']] = {
            'length': box['length'],
            'width': box['width'],
            'height': box['height'],
            'volume': box['volume']
        }

    for i in range(len(boxes)):
        boxName = boxes[i][3]
        if boxesContents[i]:
            results.append({
                'name': boxName,
                'boxVolume': boxesMap[boxName]['volume'],
                'volumeFilled': round(boxesMap[boxName]['volume'] - boxes[i][0], 3),
                'weight': round(boxes[i][1], 3),
                'contents': boxesContents[i],
                'length': boxesMap[boxName]['length'],
                'width': boxesMap[boxName]['width'],
                'height': boxesMap[boxName]['height']
            })

    return results

def displayResultsAsString(results):
    texts = []
    count = 1
    for box in results:
        contents = []
        for item in box['contents']:
            contents.append('{}-{:<8}x{}'.format(item.sku, item.uomCode, item.qty))

        texts.append('{}. Box - {} ({}" x {}" x {}")'.format(count, box['name'], box['length'], box['width'], box['height']))
        texts.append('Weight: {} Lb'.format(box['weight']))
        texts.append('Contents:\n{}'.format('\n'.join(contents)))
        texts.append(' ')
        count += 1

    return texts

def distribute(filepath):
    success = True

    # salesQuotationFilepath = validateInputFilename(filepath)

    inventoryMaster, invMsg = getInventoryMasterData('./warehouse_master.xlsx')
    boxesMaster, boxMsg = getBoxesMasterData('./boxes_master.csv')
    items, itemsMsg = getSalesQuotationItemsFromInputfile("./sq_3.xlsx")
    itemLines, itemsWithNoInfo = combineDetailsForEachItem(inventoryMaster, items)

    splittedItemLines = splitCasesAndBoxesForEachItem(itemLines)

    boxes, boxesContents, itemsDoNotFit = distributeToBoxes(boxesMaster, splittedItemLines)

    results = compileResults(boxesMaster, boxes, boxesContents)

    return {
        'success': success,
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