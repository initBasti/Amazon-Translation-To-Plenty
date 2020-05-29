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
    translation_df = prepare_barcode_value(data=translation_df,
                                           column='external_product_id')
    new_df = pandas.merge(
        new_df, translation_df[['external_product_id', 'color_name']],
        on='external_product_id', how='left')

    new_df.dropna(subset=['color_name'], inplace=True)

    attribute_df = data['attribute']
    attribute_df.dropna(subset=['AttributeValue.backendName'], inplace=True)
    new_df['attribute_id'] = new_df['color_name_german'].apply(
        lambda x: find_id_for_color(attribute_df, x))

    color_df = new_df[['attribute_id', 'color_name']]
    print("execution time: {0} us"
          .format(round(time.time()-starttime, 4)*1000000))

    return color_df

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
    print("execution time: {0} us"
          .format(round(time.time()-starttime, 4)*1000000))
    return new_frame

def text_assign(data):
    """
        Reduce the translation file to the required text upload fields.

        Parameter:
            path [str] : Path to input file

        Return:
            [DataFrame]
    """
    starttime = time.time()
    frame = data
    frame = frame[frame['parent_child'] == 'parent']
    required_columns = ['item_sku', 'product_description', 'generic_keywords']
    missing_columns = [x for x in required_columns if x not in frame.columns]
    if missing_columns:
        print(f"Flatfile doesn't contain required column/s: {missing_columns}")
        return None
    print("text assign\nexecution time: {0} us"
          .format(round(time.time()-starttime, 4)*1000000))
    return frame[required_columns]

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

    backend_match = backendname[backendname.str.match(color)]
    if len(backend_match.index) == 0:
        value_match = valuename[valuename.str.match(color)]
        if len(value_match.index) == 0:
            return numpy.nan
        return data[data[val_key] == value_match.max()][id_key].max()
    return data[data[back_key] == backend_match.max()][id_key].max()

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
    if not line:
        return None
    if re.search(r'color', line):
        if(re.search(r'size_name', line) and re.search(r',', line)):
            line_list = line.split(',')
        elif re.search(r':', line) and not re.search(r',', line):
            return line.split(':')[1]

        if len(line_list) > 2:
            for index, item in enumerate(line_list):
                if not re.search(r':', item):
                    # in case the value contains a ','
                    new_value = ','.join(line_list[index-1:index])
                    if re.search(r'color', new_value):
                        return new_value.split(':')[1]
                full_option = full_option + 1
                if full_option > 2:
                    raise TooManyOptionsError('Too many Options:{0}'
                                              .format(line))
        elif len(line_list) == 2:
            for item in line_list:
                if re.search(r'color', item):
                    return item.split(':')[1]
    return None

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
