# The MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from constants import RotationType, Axis
from auxiliary_methods import intersect, set_to_decimal
from utils import *
from config import *

DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]


class Item:
    def __init__(self, name, uom, width, height, depth, weight):
        self.name = name
        self.uom = uom
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        self.rotation_type = 0
        self.position = START_POSITION
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.weight,
            self.position, self.rotation_type, self.get_volume()
        )

    def get_volume(self):
        return set_to_decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def get_dimension(self):
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension


class Bin:
    def __init__(self, name, width, height, depth, max_weight):
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.current_weight = 0
        self.max_weight = max_weight
        self.items = []
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.index = -1

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.name, self.width, self.height, self.depth, self.max_weight,
            self.get_volume()
        )

    def get_volume(self):
        return set_to_decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )
    
    def get_filled_volume(self):
        volume = 0
        if self.items:
            for item in self.items:
                volume += set_to_decimal(item.width * item.height * item.depth, self.number_of_decimals)
        return volume

    def get_total_weight(self):
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return set_to_decimal(total_weight, self.number_of_decimals)

    def put_item(self, item, pivot):
        fit = False
        valid_item_position = item.position
        item.position = pivot

        for i in range(0, len(RotationType.ALL)):
            item.rotation_type = i
            dimension = item.get_dimension()
            if (
                self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                if self.get_total_weight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                self.current_weight += item.weight
                self.items.append(item)

            if not fit:
                item.position = valid_item_position

            return fit

        if not fit:
            item.position = valid_item_position

        return fit


class Packer:
    def __init__(self):
        self.bins = []
        self.filled_bins = []
        self.items = []
        self.unfit_items = []
        self.ship_as_is = []
        self.total_items = 0

    def add_bin(self, bin):
        return self.bins.append(bin)

    def add_item(self, item):
        self.total_items = len(self.items) + 1

        return self.items.append(item)

    # def pack_to_bin(self, bin, item):
    #     fitted = False

    #     if not bin.items:
    #         response = bin.put_item(item, START_POSITION)

    #         if not response:
    #             bin.unfitted_items.append(item)

    #         return

    #     for axis in range(0, 3):
    #         items_in_bin = bin.items

    #         for ib in items_in_bin:
    #             pivot = [0, 0, 0]
    #             w, h, d = ib.get_dimension()
    #             if axis == Axis.WIDTH:
    #                 pivot = [
    #                     ib.position[0] + w,
    #                     ib.position[1],
    #                     ib.position[2]
    #                 ]
    #             elif axis == Axis.HEIGHT:
    #                 pivot = [
    #                     ib.position[0],
    #                     ib.position[1] + h,
    #                     ib.position[2]
    #                 ]
    #             elif axis == Axis.DEPTH:
    #                 pivot = [
    #                     ib.position[0],
    #                     ib.position[1],
    #                     ib.position[2] + d
    #                 ]

    #             if bin.put_item(item, pivot):
    #                 fitted = True
    #                 break
    #         if fitted:
    #             break

    #     if not fitted:
    #         bin.unfitted_items.append(item)

    def pack_to_bin(self, bin, item):
        fitted = False

        # if bin is empty
        if not bin.items:
            response = bin.put_item(item, START_POSITION)

            if not response:
                # bin.unfitted_items.append(item)
                return fitted
            else:
                fitted = True

            return fitted
        
        # if bin has item(s)
        for axis in range(0, 3):
            items_in_bin = bin.items

            for ib in items_in_bin:
                pivot = [0, 0, 0]
                w, h, d = ib.get_dimension()
                if axis == Axis.WIDTH:
                    pivot = [
                        ib.position[0] + w,
                        ib.position[1],
                        ib.position[2]
                    ]
                elif axis == Axis.HEIGHT:
                    pivot = [
                        ib.position[0],
                        ib.position[1] + h,
                        ib.position[2]
                    ]
                elif axis == Axis.DEPTH:
                    pivot = [
                        ib.position[0],
                        ib.position[1],
                        ib.position[2] + d
                    ]

                if bin.put_item(item, pivot):
                    fitted = True
                    break
            if fitted:
                break

        # if not fitted:
        #     bin.unfitted_items.append(item)

        return fitted
    
    def pack(
        self, bins_bigger_first=False, items_bigger_first=False, distribute_items=False,
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS
    ):
        for bin in self.bins:
            bin.format_numbers(number_of_decimals)

        for item in self.items:
            item.format_numbers(number_of_decimals)

        self.bins.sort(
            key=lambda bin: bin.get_volume(), reverse=bins_bigger_first
        )
        self.items.sort(
            key=lambda item: item.get_volume(), reverse=items_bigger_first
        )

        # for bin in self.bins:
        #     print(bin.string())

        # New algorithm for packing efficiency
        for idx, item in enumerate(self.items):
            itemIsFitted = False

            # check if item should be shipped as is
            if item.uom == "CASE" and item.weight >= SHIP_CASE_AS_IS_WEIGHT_THRESHOLD:
                self.ship_as_is.append(item)
                continue

            # try to fit item in a filled bin
            for filled_bin in self.filled_bins:
                canFitToBiggerBin = False
                # if filled_bin is not an active bin
                if not filled_bin.items:
                    continue

                # if item fits in current filled bin
                if self.pack_to_bin(filled_bin, item):
                    itemIsFitted = True
                    break

                # check if we can combine item(s) from previous box with current item in a bigger box
                nextBiggerBin = None
                nextBinIndex = filled_bin.index + 1
                while (not itemIsFitted and nextBinIndex < len(self.bins)):
                    if nextBinIndex < len(self.bins):
                        nextBiggerBin = self.bins[nextBinIndex]
                    
                    if nextBiggerBin:
                        # check if current item is the last item, and the filled bin volume combined with the smallest box volume, is smaller than the next bigger bin volume.
                        if (idx == len(self.items) - 1) and (filled_bin.get_volume() + self.bins[0].get_volume() < nextBiggerBin.get_volume()):
                            break
                            
                    for _item in filled_bin.items:
                        if not self.pack_to_bin(nextBiggerBin, _item):
                            nextBiggerBin.items = []
                            break

                    if self.pack_to_bin(nextBiggerBin, item):
                        biggerBin = Bin(nextBiggerBin.name, nextBiggerBin.width, nextBiggerBin.height, nextBiggerBin.depth, nextBiggerBin.max_weight)
                        biggerBin.items = nextBiggerBin.items
                        biggerBin.index = self.bins.index(nextBiggerBin)
                        self.filled_bins.append(biggerBin)
                        nextBiggerBin.items = []
                        filled_bin.items = [] # deactivate filled_bin
                        itemIsFitted = True
                        canFitToBiggerBin = True

                    nextBinIndex += 1

                if canFitToBiggerBin:
                    break

            # if no filled bins or item does not fit in any filled bins, put item in an empty bin
            if not itemIsFitted:
                for bin in self.bins:
                    if self.pack_to_bin(bin, item):
                        itemIsFitted = True
                        filledBin = Bin(bin.name, bin.width, bin.height, bin.depth, bin.max_weight)
                        filledBin.items = bin.items
                        filledBin.index = self.bins.index(bin)
                        bin.items = []
                        self.filled_bins.append(filledBin)
                        break
            
            if not itemIsFitted:
                self.ship_as_is.append(item)

        return self.ship_as_is
