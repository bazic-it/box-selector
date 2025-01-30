import os
import csv
import pandas as pd
import openpyxl
import math
from functools import cmp_to_key
from utils import *
from config import *
from classes import *
from packer_main import Packer, Bin, Item


def registerBoxesToPacker(packer, boxes):
    for box in boxes:
        bin = Bin(box.name, box.length, box.width, box.height, MAX_WEIGHT_PER_BOX)
        packer.add_bin(bin)

def registerItemsToPacker(packer, items):
    for _item in items:
        item = Item(_item.sku, _item.uomCode, _item.length, _item.width, _item.height, _item.weight)
        packer.add_item(item)

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
    message = None
    targetColumns = ['Item No.', 'Available Qty', 'Case Length', 'Case Width', 'Case Height', 'Case Volume', 'Case Weight', 'Box Length', 'Box Width', 'Box Height', 'Box Volume', 'Box Weight', 'EA Length', 'EA Width', 'EA Height', 'EA Volume', 'EA Weight']
    keyColumn = 'Item No.'
    headerMap = {}
    mapped = {}

    try:
        age = getDaysDifferent(getCurrentime(), getFileModifiedDate(inputFilepath))
        message = 'Inventory master file was updated {} days ago.'.format(age)

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
    message = None
    targetColumns = ['Item No.', 'Item Description', 'UoM Code', 'Quantity', 'Price Per Piece', 'Total (LC)', 'Unit Price', 'Available Qty']
    headerMap = {}
    items = []
    
    try:
        age = getDaysDifferent(getCurrentime(), getFileModifiedDate(filepath))
        message = 'Inventory master file was updated {} days ago.'.format(age)

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
                length = float(line[1]) - BOX_DIMENSION_PADDING
                width = float(line[2]) - BOX_DIMENSION_PADDING
                height = float(line[3]) - BOX_DIMENSION_PADDING
                weight = float(line[4])
                box = Box(line[0], length, width, height, weight)
                boxes.append(box)
                row += 1
    except Exception as e:
        print(f'*** Error: Failed to read input file for Boxes Master Data. Please make sure filename is valid. {e} ***')
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

def splitItem(itemLines):
    newItemLines = []

    for item in itemLines:
        # if item.uomCode == 'CASE' and item.qty > 1:
        if item.qty > 1:
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

def itemFitByDimension(boxLength, boxWidth, boxHeight, itemLength, itemWidth, itemHeight):
    failCondition1 = itemLength > boxLength or itemWidth > boxWidth or itemHeight > boxHeight
    failCondition2 = itemWidth > boxLength or itemHeight > boxWidth or itemLength > boxHeight
    failCondition3 = itemHeight > boxLength or itemLength > boxWidth or itemWidth > boxHeight

    if failCondition1 and failCondition2 and failCondition3:
        return False
    return True

def distributeToBoxes(boxes, itemLines):
    # Sort items from highest volume to lowest volume
    itemLines.sort(key=lambda i:i.volume, reverse=True)
    # Sort boxes from lowest volume to highest volume
    boxes = sortBoxes(boxes)

    # for b in boxes:
    #     print(b)

    activeBoxes = [] # [current remaining box volume, current box total weight, box weight, box name, box index, box length, box width, box height]
    activeBoxesContent = []
    itemsDoNotFit = []
    itemsShipAsIs = []

    for item in itemLines:
        # decide if want to ship Case as is (without outer box)
        if item.uomCode == 'CASE' and item.weight >= SHIP_CASE_AS_IS_WEIGHT_THRESHOLD:
            itemsShipAsIs.append(item)
            continue

        foundABox = False
        itemTotalVolume = item.volume * item.qty
        itemTotalWeight = item.weight * item.qty
        # look at previous boxes
        if activeBoxes:
            for i in range(len(activeBoxes)):
                activeBoxRemainingVolume = activeBoxes[i][0]
                activeBoxTotalWeight = activeBoxes[i][1]
                activeBoxWeight = activeBoxes[i][2]
                activeBoxesLength = activeBoxes[i][5]
                activeBoxesWidth = activeBoxes[i][6]
                activeBoxesHeight = activeBoxes[i][7]
                # if item fits in a previous box
                if activeBoxes[i][0] >= itemTotalVolume and activeBoxes[i][1] + itemTotalWeight < MAX_WEIGHT_PER_BOX and itemFitByDimension(activeBoxesLength, activeBoxesWidth, activeBoxesHeight, item.length, item.width, item.height):
                    activeBoxes[i][0] -= itemTotalVolume
                    activeBoxes[i][1] += itemTotalWeight
                    activeBoxesContent[i].append(item)
                    foundABox = True
                    break
                # check if we can combine item(s) from previous box with current item in a bigger box
                nextBoxIndex = activeBoxes[i][4] + 1
                currentBoxTotalVolume = boxes[activeBoxes[i][4]]['volume'] - activeBoxRemainingVolume
                currentBoxTotalWeight = activeBoxTotalWeight
                while currentBoxTotalVolume + itemTotalVolume > boxes[nextBoxIndex]['volume'] and nextBoxIndex < len(boxes) - 1:
                    nextBoxIndex += 1
                if activeBoxes[i][0] != -1 and nextBoxIndex >= 0 and nextBoxIndex < len(boxes) - 1:
                    nextBox = boxes[nextBoxIndex]
                    currentBoxWeight = activeBoxWeight
                    newBoxWeight = nextBox['weight'] - currentBoxWeight
                    if (currentBoxTotalVolume + itemTotalVolume <= nextBox['volume']) and (currentBoxTotalWeight + itemTotalWeight + newBoxWeight < MAX_WEIGHT_PER_BOX) and (itemFitByDimension(activeBoxesLength, activeBoxesWidth, activeBoxesHeight, item.length, item.width, item.height)) and (not volumeIsBiggerByAtLeast(VOLUME_BIGGER_BY_THRESHOLD, nextBox['volume'], boxes[activeBoxes[i][4]]['volume'])):
                        activeBoxes.append([nextBox['volume'] - (currentBoxTotalVolume + itemTotalVolume), currentBoxTotalWeight + itemTotalWeight + newBoxWeight, nextBox['weight'], nextBox['name'], nextBoxIndex, nextBox['length'], nextBox['width'], nextBox['height']])
                        activeBoxesContent.append([item] + activeBoxesContent[i])
                        activeBoxes[i][0] = -1
                        activeBoxesContent[i] = []
                        foundABox = True
                        break
        # find a new box
        if not foundABox:
            for i in range(len(boxes)):
                if itemTotalVolume <= boxes[i]['volume'] and itemTotalWeight + boxes[i]['weight'] < MAX_WEIGHT_PER_BOX and itemFitByDimension(boxes[i]['length'], boxes[i]['width'], boxes[i]['height'], item.length, item.width, item.height):
                    activeBoxes.append([boxes[i]['volume'] - itemTotalVolume, itemTotalWeight + boxes[i]['weight'], boxes[i]['weight'], boxes[i]['name'], i, boxes[i]['length'], boxes[i]['width'], boxes[i]['height']])
                    activeBoxesContent.append([item])
                    foundABox = True
                    break
        # item could not find a box
        if not foundABox:
            itemsDoNotFit.append(item.sku)

        print("***********************")
        print(activeBoxes)
        for c in activeBoxesContent:
            print("box")
            for i in c:
                print(i)

    return activeBoxes, activeBoxesContent, itemsShipAsIs, itemsDoNotFit

def compileResults(boxesMaster, boxes, boxesContents, itemsShipAsIs):
    results = []
    boxesMap = {}

    for box in boxesMaster:
        boxesMap[box['name']] = {
            'length': box['length'],
            'width': box['width'],
            'height': box['height'],
            'volume': box['volume']
        }

    for item in itemsShipAsIs:
        results.append({
            'name': item.sku + '-' + item.uomCode,
            'boxVolume': item.volume,
            'volumeFilled': item.volume,
            'weight': item.weight,
            'contents': '-',
            'length': item.length,
            'width': item.width,
            'height': item.height,
            'type': 'as_is'
        })

    for i in range(len(boxes)):
        boxName = boxes[i][3]
        if boxesContents[i]:
            # consolidate content based on qty
            consolidatedContents = {}
            for content in boxesContents[i]:
                key = content.sku + '-' + content.uomCode
                if key in consolidatedContents:
                    consolidatedContents[key]['qty'] += 1
                else:
                    consolidatedContents[key] = {
                        'sku': content.sku,
                        'uomCode': content.uomCode,
                        'qty': 1,
                        'length': content.length,
                        'width': content.width,
                        'height': content.height,
                        'volume': content.volume,
                        'weight': content.weight
                    }

            results.append({
                'name': boxName,
                'boxVolume': boxesMap[boxName]['volume'],
                'volumeFilled': round(boxesMap[boxName]['volume'] - boxes[i][0], 3),
                'weight': round(boxes[i][1], 3),
                'contents': consolidatedContents,
                'length': boxesMap[boxName]['length'],
                'width': boxesMap[boxName]['width'],
                'height': boxesMap[boxName]['height'],
                'type': 'outer_box'
            })

    return results

# def displayResultsAsString(results):
#     texts = []
#     count = 1

#     for result in results:
#         if result['type'] == 'outer_box':
#             box = result
#             contents = []
#             for contentKey, contentValues in box['contents'].items():
#                 contents.append('{}-{:<8}x{}'.format(contentValues['sku'], contentValues['uomCode'], contentValues['qty']))

#             texts.append('{}. Box: {} ({}" x {}" x {}")'.format(count, box['name'], box['length'] + BOX_DIMENSION_PADDING, box['width'] + BOX_DIMENSION_PADDING, box['height'] + BOX_DIMENSION_PADDING))
#             texts.append('Weight: {} Lb'.format(math.ceil(box['weight'])))
#             texts.append('Contents:\n{}'.format('\n'.join(contents)))
#             texts.append(' ')
#         elif result['type'] == 'as_is':
#             texts.append('{}. As Is: {} ({}" x {}" x {}")'.format(count, result['name'], result['length'], result['width'], result['height']))
#             texts.append('Weight: {} Lb'.format(math.ceil(result['weight'])))
#             texts.append(' ')
#         else:
#             pass

#         count += 1

#     return texts

def compileItemsInBox(items):
    mapped = {}

    for item in items:
        key = item.name + "-" + item.uom
        if key in mapped:
            mapped[key]["qty"] += 1
        else:
            mapped[key] = {
                "name": item.name,
                "uom": item.uom,
                "qty": 1,
                "width": item.width,
                "height": item.height,
                "depth": item.depth
            }

    return mapped

def displayResultsAsString(boxes, itemsWithoutOuterBox):
    texts = []
    count = 1

    for box in boxes:
        if box.items:
            compiledItems = compileItemsInBox(box.items)
            texts.append('{}. {}    ({}" x {}" x {}")'.format(count, box.name, float(box.width) + BOX_DIMENSION_PADDING, float(box.height) + BOX_DIMENSION_PADDING, float(box.depth) + BOX_DIMENSION_PADDING))
            texts.append('    Volume: {} / {}   Weight: {} Lbs'.format(box.get_filled_volume(), box.get_volume(), box.current_weight))
            texts.append('    Content:')
            for _, item in compiledItems.items():
                texts.append('    {}x   {} - {} ({}" x {}" x {}")'.format(item["qty"], item["name"], item["uom"], item["width"], item["height"], item["depth"]))
            texts.append('')
            count += 1

    if itemsWithoutOuterBox:
        texts.append('Ship As Is:')
        for item in itemsWithoutOuterBox:
            texts.append('    {} - {} ({}" x {}" x {}")'.format(item.name, item.uom, item.width, item.height, item.depth))

    return texts

def distribute(filepath):
    packer = Packer()
    success = True

    salesQuotationFilepath = validateInputFilename(filepath)

    inventoryMaster, invMsg = getInventoryMasterData(getInventoryMasterFilepath())
    boxesMaster, boxMsg = getBoxesMasterData(getBoxMasterFilepath())
    items, itemsMsg = getSalesQuotationItemsFromInputfile(salesQuotationFilepath)
    itemLines, itemsWithNoInfo = combineDetailsForEachItem(inventoryMaster, items)
    splittedItemLines = splitItem(itemLines)

    registerItemsToPacker(packer, splittedItemLines)
    registerBoxesToPacker(packer, boxesMaster)

    leftoverItems = packer.pack(bins_bigger_first=False, items_bigger_first=True, distribute_items=True, number_of_decimals=2)

    # for b in packer.bins:
    #     print(":::::::::::", b.string())

    #     print("FITTED ITEMS:")
    #     for item in b.items:
    #         print("====> ", item.string())

    #     print("UNFITTED ITEMS:")
    #     for item in b.unfitted_items:
    #         print("====> ", item.string())

    #     print("***************************************************")
    #     print("***************************************************")


    # print("Items List:")
    # for item in splittedItemLines:
    #     print(item)

    # boxes, boxesContents, itemsShipAsIs, itemsDoNotFit = distributeToBoxes(boxesMaster, splittedItemLines)

    # results = compileResults(boxesMaster, boxes, boxesContents, itemsShipAsIs)
    results = displayResultsAsString(packer.filled_bins, leftoverItems)

    return {
        'success': success,
        'results': results
    }

def validateInputFilename(filename):
    cleaned = filename
    if '/' in filename:
        cleaned = filename.split('/')[-1]

    if '.xlsx' not in cleaned:
        cleaned = cleaned + '.xlsx'

    return USER_DOWNLOADS + cleaned

# def writeLog(timestamp, status):
#     path = os.path.join(ASSETS_BASE_DIR, LOGS_FILENAME)
#     user = os.getenv('COMPUTERNAME')
#     try:
#         with open(path, 'a') as file:
#             file.write('USR;{} | IN;{} | SUCCESS;{} | ERR;{} | WARNING;{} | WARN;{} | OOS;{} | OUT;{} | VER;{} | TS;{}\n'.format(user, status["inputFilename"], status["success"], status["errorMessage"], status["warning"], status["warningMessage"], status["outOfStockSKUs"], status["outputFilename"], APP_VERSION, timestamp))
#     except:
#         print('*** Error: Failed to write to logs. ***')