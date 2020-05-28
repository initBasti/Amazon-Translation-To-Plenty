import sys
import os
import chardet
import re
import time
import pandas
import numpy
import csv
from collections import OrderedDict as Odict
from tkinter import filedialog as fd
from tkinter import messagebox as tmb


class TooManyOptionsError(Exception):
    def __init__(self, message):
        super().__init__(message)


class WrongFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)

pandas.options.mode.chained_assignment = None

def findFile(path):
    """
        Search in a given folder for any file in the format of
        translation_xxx.csv, if there is no hit open a file dialog.

        Parameter:
            path [String] : Path of the specified folder

        Return:
            outputfile [String] : Path of the file
    """
    outputfile = ''
    files = list()
    try:
        for(dirpath, dirnames, filenames) in os.walk(path):
            files.extend(filenames)
    except Exception as err:
        print("Error @ line: {0} | Getting the files as a list!\nError: {1}\n"
              .format(sys.exc_info()[2].tb_lineno, err))

    if(len(files) == 0):
        tmb.showerror("No input error!",
                      "There is no input file, in the Input folder")
        sys.exit(1)

    for i in range(len(files)):
        if(re.search(r'\btranslation_\w+.csv\b', files[i])):
            outputfile = os.path.join(path, files[i])
    if not outputfile:
        outputfile = fd.askopenfilename(title="Translation file",
                                        initialdir=path)

    return outputfile


def color_assign(data):
    """
        Map the PlentyMarkets attribute-value ID to the translated
        color value of each Sku found in the Translate file.
        Create an upload file for the Elastic Sync(Import) tool.

        Parameter:
            files [dict] : Dictionary of Dataframes

        Return:
            color_df [DataFrame] : Color ID and new Value for the import
    """
    starttime = time.time()
    new_df = ''
    connect_df = data['connect']

    connect_df = connect_df[connect_df['Variation.isMain'] == 0]
    connect_df = connect_df[connect_df['VariationBarcode.code'].notna()]
    connect_df['color_name_german'] =\
        connect_df['VariationAttributeValues.attributeValues'].apply(
            parse_color_value)
    new_df = pandas.concat(
        [connect_df['VariationBarcode.code'],
         connect_df['color_name_german']], axis=1)
    new_df.rename(columns={'VariationBarcode.code':'external_product_id'},
                  inplace=True)
    new_df = prepare_barcode_value(data=new_df,
                                   column='external_product_id')

    translation_df = data['translation'].astype({'item_sku':object})
    translation_df =  prepare_barcode_value(data=translation_df,
                                            column='external_product_id')
    new_df = pandas.merge(
        new_df, translation_df[['external_product_id', 'color_name']],
        on='external_product_id', how='left')

    new_df.dropna(subset=['color_name'], inplace=True)

    attribute_df = data['attribute']
    new_df['attribute_id'] = new_df['color_name_german'].apply(
        lambda x: find_id_for_color(attribute_df, x))

    color_df = new_df[['attribute_id', 'color_name']]
    endtime = time.time()
    print("execution time: {0} us"
          .format(round(endtime-starttime, 4)*1000000))

    return color_df


def find_id_for_color(data, color):
    """
        Search for a match between the parsed color value for a variation
        and the backend name or value name of the color attributes
        within the Plentymarkets attribute export.

        Parameter:
            data [DataFrame] : Attribute Export as Dataframe
            color [String] : color value [original language] for variation

        Return:
            [String] : ID of the backend entry for the color or NaN
    """
    back_key = 'AttributeValue.backendName'
    val_key = 'AttributeValueName.name'
    id_key = 'AttributeValue.id'
    backendname = data[back_key]
    valuename = data[val_key]

    backend_match = backendname[backendname.str.match(color)==True]
    if len(backend_match.index) == 0:
        value_match = valuename[valuename.str.match(color)==True]
        if len(value_match.index) == 0:
            return numpy.nan
        else:
            return data[data[val_key] == value_match.max()][id_key].max()
    else:
        return data[data[back_key] == backend_match.max()][id_key].max()

def checkEncoding(data):
    raw_data = ''
    for index, opt in enumerate([*data]):
        try:
            with open(data['path'], mode='rb') as item:
                raw_data = item.read(50000)
            data['encoding'] = chardet.detect(raw_data)['encoding']
        except Exception as err:
            print("Error @ line: {0} | Error at encode check\nError: {1}|{2}\n"
                  .format(sys.exc_info()[2].tb_lineno, err,
                          data['path']))

        if(not(data['encoding'])):
            data['encoding'] = 'utf-8'

    return data


def parse_color_value(line):
    """
        Retrieve the mapped attribute for a given variation by parsing
        the attribute value string. The string has a format of:
            'color:xxxx,size_name:xxx' or
            'color:xxxx'

        Parameter:
            line [string] : VariationAttributeValues.attributeValues field
                            from the Plentymarkets Export

        Return:
            [string] : the color value or "None"
    """
    line_list = []
    full_option = 0
    if(not(line)):
        return None
    if(re.search(r'color', line)):
        if(re.search(r'size_name', line) and re.search(r',', line)):
            line_list = line.split(',')
        else:
            if(re.search(r':', line) and not(re.search(r',', line))):
                return line.split(':')[1]

        if(len(line_list) > 2):
            for i in range(len(line_list)):
                if(not(re.search(r':', line_list[i]))):
                    # in case the value contains a ','
                    new_value = ','.join(line_list[i-1:i])
                    if(re.search(r'color', new_value)):
                        return new_value.split(':')[1]
                else:
                    full_option = full_option + 1
                if(full_option > 2):
                    raise TooManyOptionsError('Too many Options:{0}'
                                              .format(line))
        elif(len(line_list) == 2):
            for i in range(2):
                if(re.search(r'color', line_list[i])):
                    return line_list[i].split(':')[1]
    elif(not(re.search(r'color', line))):
        return None



def ColorTranslateValue(variation, sku, color):
    if(re.match(variation, sku, re.IGNORECASE)):
        return color
    else:
        raise WrongFormatError('The file has the wrong header')

    return None

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
    starttime = time.time()

    df = data

    required_columns = id_fields.keys()
    missing_columns = [x for x in required_columns if x not in df.columns]
    if missing_columns:
        print(f"Flatfile doesn't contain column/s: {missing_columns}")
    columns = [x for x in required_columns if x in df.columns]

    for col in columns:
        col_id = id_fields[col]
        row = [[x, col_id, y, lang] for x, y in zip(df['item_sku'], df[col])]
        for element in row:
            row_list.append(element)

    new_df = pandas.DataFrame(row_list, columns=['sku', 'id', 'value', 'lang'])

    new_df.dropna(subset=['value'], inplace=True)
    new_df = new_df[new_df['value'] != ' '].reset_index(drop=True)
    endtime = time.time()
    print("execution time: {0} us"
          .format(round(endtime-starttime, 4)*1000000))
    return new_df

def text_assign(data):
    """
        Reduce the translation file to the required text upload fields.

        Parameter:
            path [str] : Path to input file

        Return:
            [DataFrame]
    """
    starttime = time.time()
    df = data
    df = df[df['parent_child'] == 'parent']
    required_columns = ['item_sku', 'product_description', 'generic_keywords']
    missing_columns = [x for x in required_columns if x not in df.columns]
    if missing_columns:
        print(f"Flatfile doesn't contain required column/s: {missing_columns}")
        return None
    endtime = time.time()
    print("text assign\nexecution time: {0} us"
          .format(round(endtime-starttime, 4)*1000000))
    return df[required_columns]

def find_duplicates(target_df, column):
    """
        Remove entries with duplicate attribute value IDs

        Parameter:
            target_df [DataFrame]

        Return:
            target_df (unique) [DataFrame]
    """
    return target_df[target_df[column] == target_df[column].unique()]

def prepare_barcode_value(data, column):
    """
        Remove empty strings and NaN values from the barcode column
        Convert the column to an integer type.

        Parameter:
            data [DataFrame] : Input file to prepare
            column [String] : specific column

        Return:
            [DataFrame] : clean dataframe
    """
    data[column] = data[column].replace([' ', ''], numpy.nan)
    return data[data[column].notna()].reset_index().astype({column:int})
