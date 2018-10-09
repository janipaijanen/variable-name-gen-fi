#!/usr/bin/env python3
# encoding: utf-8
# (C) Copyright 2018 Jani Päijänen
import argparse
import os, sys
import openpyxl
from openpyxl import load_workbook
import logging
import pprint

class FormatPrinter(pprint.PrettyPrinter):

    def __init__(self, formats):
        super(FormatPrinter, self).__init__()
        self.formats = formats

    def format(self, obj, ctx, maxlvl, lvl):
        if type(obj) in self.formats:
            return self.formats[type(obj)] % obj, 1, 0
        return pprint.PrettyPrinter.format(self, obj, ctx, maxlvl, lvl)

def find_duplicates(wb:openpyxl.workbook, male_sheetname, female_sheetname) -> [] :
    logger = logging.getLogger(__name__)
    # return: list of duplicate names, e.g. can be given either to a girl or a boy
    males = []
    males_dict = {}
    female_dups = []

    male_max = 0
    male_total = 0

    female_max = 0
    female_min = None
    female_total = 0

    logger.info("find dups")

    header_done = False
    males = ()

    for row in wb[male_sheetname].iter_rows():
        name = None
        count = 0

        if header_done == False:
            header_done = True
            continue

        for cell in row:
            if name is None:
                name = cell.value
            else:

                count = cell.value
                male_total = male_total + count

                if count > male_max:
                    male_max = count
                    male_total = male_total + count

        males_dict[name] = count

    logger.debug("male max: {}".format(male_max))
    logger.debug("male total: {}".format(male_total))

    dict_female_dups = {}
    females = []

    male_dup_max = 0

    for row in wb[female_sheetname].iter_rows():
        name = None
        count = 0

        neutral_name = False
        column=-1

        for cell in row:
            column += 1
            if cell.value in males_dict:
                name = cell.value
                neutral_name = True


            if column == 0:
                if neutral_name == False:
                    females.append(cell.value)

                continue


            if name is not None:
                count = cell.value
                female_total = female_total + count

                if count > female_max:
                    female_max = count

                if female_min is None:
                    female_min = count
                elif count < female_min:
                    female_min = count

                if males_dict[name] > male_dup_max:
                    male_dup_max = males_dict[name]


        if name is not None:
            #logger.debug("{}:{}".format(name, count))
            female_dups.append( (name, count)  )

    logger.debug ("female_min: {}".format(female_min))
    logger.debug ("female_max: {}".format(female_max))
    logger.debug ("male_dup_max: {}".format(male_dup_max))

    scales = {}
    scale_max = None
    scale_min = None
    name_max = None
    name_min = None

    for (name, count) in female_dups:
        duh = males_dict[name] / count * 1.0
        scales[name] = duh

        if scale_max is None:
            scale_max = duh
            name_max = name
        elif duh > scale_max:
            scale_max = duh
            name_max = name

        if scale_min is None:
            scale_min = duh
            name_min = name
        elif duh < scale_min:
            scale_min = duh
            name_min = name

    logger.debug("scale_min {:+.6f}, scale_max {:+.6f}".format(scale_min, scale_max))
    logger.debug("name_min {}, name_max {}".format(name_min, name_max))

    # As zero is female value and one is male value,
    # we want to distinquish gender neutral names from gender directed weighted.
    min_target = 0.001
    max_target = 0.99

    for (name, count) in female_dups:

        dict_female_dups[name] = (
                # scales to (0 .. 1) and works ok, but we need something else
                #( scales[name] - scale_min) / (scale_max - scale_min)

                # scales to (0.05 .. 0.95) https://en.wikipedia.org/wiki/Normalization_(statistics)
                min_target + ((scales[name] - scale_min) * (max_target - min_target) ) / (scale_max - scale_min)

            )

    for name in dict_female_dups:
        yield (name, dict_female_dups[name])

    for name in females:
        yield (name, 0.0)

    for name in males_dict:
        if name not in female_dups:
            yield (name, 1.0)

def process_gender(wb:openpyxl.workbook, sheetname:str ) -> {}:
    total = 0
    # return {str:float}
    # count total
    # read row, count %

    pass

def process_input_file(filename:str) -> None:
    pass
    wb = load_workbook(filename, read_only=True)

    ws_malename = "Miehet kaikki"
    ws_femalename = "Naiset kaikki"

    ws = wb[ws_malename]
    ws = wb[ws_femalename]
    ws = None

    # Column A: Given name
    # Column B: Name count

    for (name, value) in find_duplicates(wb, male_sheetname=ws_malename, female_sheetname=ws_femalename):
        FormatPrinter({float: "%.6f", int: "%06X"}).pprint( (name, value))

    #print ("female duplicates over males: {}".format(dups))
    #process_gender(wb, ws_malename)

def main():
    format='%(levelname)s:%(message)s'
    logging.basicConfig(format=format, level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, default=None, help="input file provided by Finnish Population Register Centre")
    args = parser.parse_args()

    if args.input_file is None or os.path.isfile(args.input_file) is False:
        parser.print_usage()
        sys.exit()

    process_input_file(args.input_file)


if __name__ == '__main__':
    main()
