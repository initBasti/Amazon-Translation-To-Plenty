"""
    Author: Sebastian Fricke
    Date: 28-05-2020
    License: GPLv3

    Assign the values from the translation file to the correct
    object IDs in PlentyMarkets.
"""
import re
import time
import numpy
import pandas


class TooManyOptionsError(Exception):
    """
        Custom exception for parse_color_value, triggered when a
        Product contains more than 3 attribute dimensions.
    """

pandas.options.mode.chained_assignment = None

def mapping_assign(data, lang, id_fields):
    """
        Map the Plentymarkets feature/proprty ID to the predefined field
        from the Translation file and format the data appropriately for an
        elastic sync(import) file.

        Parameter:
            data [DataFrame] : Translation file dataframe
            lang [String] : abbreviation for the language CLI parameter
            id_fields [Dict] : Dictionary from the config with mappings
                                for Plentymarkets Feature IDs and
                                spreadsheet column names

        Return:
            [DataFrame]
    """
    row_list = []

    frame = data

    required_columns = id_fields.keys()
    missing_columns = [x for x in required_columns if x not in frame.columns]
    if missing_columns:
        print(f"Flatfile doesn't contain column/s: {missing_columns}")
    columns = [x for x in required_columns if x in frame.columns]

    for column in columns:
        mapping_id = id_fields[column]
        sku_and_column = zip(frame['item_sku'], frame[column])
        row = [[x, mapping_id, y, lang] for x, y in sku_and_column]
        for element in row:
            row_list.append(element)

    new_frame = pandas.DataFrame(row_list, columns=['sku', 'id', 'value', 'lang'])

    new_frame.dropna(subset=['value'], inplace=True)
    new_frame = new_frame[new_frame['value'] != ' '].reset_index(drop=True)
    return new_frame

def text_assign(data):
    """
        Reduce the translation file to the required text upload fields.

        Parameter:
            path [str] : Path to input file

        Return:
            [DataFrame]
    """
    frame = data
    frame = frame[frame['parent_child'] == 'parent']
    required_columns = ['item_sku', 'product_description', 'generic_keywords']
    missing_columns = [x for x in required_columns if x not in frame.columns]
    if missing_columns:
        print(f"Flatfile doesn't contain required column/s: {missing_columns}")
        return None
    return frame[required_columns]
