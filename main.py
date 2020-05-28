import platform
import os
from collections import OrderedDict as Odict
import sys
import datetime
import tkinter
import argparse
import configparser
import pandas
from io import StringIO
from tkinter import messagebox as tmb
from packages.assignment import (
    findFile, color_assign, mapping_assign,
    text_assign, find_duplicates, checkEncoding)
from packages.writefile import writeFile
from packages.cache import WebCache

def read_data(data):
    input_frames = {'translation': '', 'attribute':'', 'connect':''}

    df = pandas.read_csv(data['translation']['path'], sep=';')
    if not 'item_sku' in df.columns or not 'color_name' in df.columns:
        df = pandas.read_csv(data['translation']['path'], sep=';',
                             header=2)
        if not 'item_sku' in df.columns or not 'color_name' in df.columns:
            print("ERROR: Input file has to be a Amazon flatfile")
            return None
    input_frames['translation'] = df

    df = pandas.read_csv(data['attribute']['content'], sep=';')
    columns = {'AttributeValue.backendName', 'AttributeValueName.name',
                'AttributeValue.id'}
    missing_columns = [x for x in columns if x not in df.columns]
    if missing_columns:
        print(f"ERROR: attribute file needs the columns: {missing_columns}")
        return None
    input_frames['attribute'] = df

    df = pandas.read_csv(data['connect']['content'], sep=';')
    columns = {'VariationAttributeValues.attributeValues',
               'VariationBarcode.code'}
    missing_columns = [x for x in columns if x not in df.columns]
    if missing_columns:
        print(f"ERROR: colorconnect file needs the columns: {missing_columns}")
        return None
    input_frames['connect'] = df

    return input_frames

def main():
    inputpath = ''
    outputpath = ''
    inputfiles = {
        'attribute':{'path':'', 'encoding':'', 'content':''},
        'translation':{'path':'', 'encoding':''},
        'connect':{'path':'', 'encoding':'', 'content':''}}
    outputfile = ''
    todaystr = ''
    attribute_name = ''
    property_name = ''
    feature_name = ''
    text_name = ''
    name = ''
    lang = ''

    root = tkinter.Tk()
    root.withdraw()

    parser = argparse.ArgumentParser(description='lang value')
    parser.add_argument('--l', '--lang', action='store',
                        choices=['en', 'fr', 'it', 'es'], required=True)
    parser.add_argument('--clean', dest='clean', default=False,
                        action='store_true', required=False,
                        help='clean the cache')
    parser.add_argument('--page-db', dest='page_db_path',
                        default='cache/page_db.db', required=False,
                        help='Location of the page database')
    parser.add_argument('--time-db', dest='time_db_path',
                        default='cache/time_db.db', required=False,
                        help='Location of the time database')
    parser.add_argument('--ttl', dest='ttl', default='3600',
                        required=False, help='Time to live of every entry')
    args = parser.parse_args()
    lang = args.l
    page_db_path = args.page_db_path
    time_db_path = args.time_db_path
    ttl = args.ttl
    clean = args.clean

    config = configparser.ConfigParser()
    config.read('config.ini')
    if not config.sections():
        print(f"config.ini required\n{err}")
        exit(1)
    feature_fields = config['FEATURE']
    property_fields = config['PROPERTY']


    # =========================================================================
    # checking the os of the user to get the correct path of the in-/out-put
    # files
    # =========================================================================
    if(platform.system() == 'Linux'):
        try:
            inputpath = os.path.join(os.getcwd(), 'Input')
            outputpath = os.path.join(os.getcwd(), 'Output')
        except Exception as err:
            print("Error @ line : {0} Linux path creation\nError: {1}\n"
                  .format(sys.exc_info()[2].tb_lineno, err))

    else:
        # =====================================================================
        # If the system is not linux than the current version only has
        # executables for windows so in that case the current working directory
        # in /Windows_Version/~Script-Name~
        # for increased orientation all the user related activities happen in
        # /Windows_Version
        # =====================================================================
        try:
            inputpath = os.path.join(os.path.join(os.getcwd(), os.pardir),
                                     'Input')
            outputpath = os.path.join(os.path.join(os.getcwd(), os.pardir),
                                      'Output')
        except Exception as err:
            print("Error @ line : {0} Windows path creation\nError: {1}\n"
                  .format(sys.exc_info()[2].tb_lineno, err))

    inputfiles['attribute']['path'] = config['URL']['attribute_export']
    inputfiles['connect']['path'] = config['URL']['variation_attribute_mapping']
    inputfiles['translation']['path'] = findFile(path=inputpath)
    inputfiles['translation'] = checkEncoding(data=inputfiles['translation'])

    cache = WebCache(page_database_path=page_db_path,
                     time_database_path=time_db_path,
                     cache_ttl=ttl)
    if clean is True:
        cache.clean()

    attr_bin = cache.get_page(
        url=inputfiles['attribute']['path'].encode('utf-8'))
    connect_bin = cache.get_page(
        url=inputfiles['connect']['path'].encode('utf-8'))
    inputfiles['attribute']['content'] = StringIO(str(attr_bin, 'utf-8'))
    inputfiles['connect']['content'] = StringIO(str(connect_bin, 'utf-8'))

    input_frames = read_data(data=inputfiles)
    if not input_frames:
        sys.exit(1)

    if(os.path.exists(inputpath) and os.path.exists(outputpath)):
        try:
            todaystr = datetime.datetime.now().strftime("%d-%m-%Y")
            name = lang + '_' + todaystr + '.csv'
        except Exception as err:
            print("Error @ line : {0} date and filename\n{1}\n"
                    .format(sys.exc_info()[2].tb_lineno, err))

        color_df = color_assign(data=input_frames)
        if len(color_df.index) != 0:
            attribute_name = os.path.join(outputpath, 'attribute_' + name)
            color_df.to_csv(attribute_name, sep=';', index=False)

        print("property mapping")
        property_df = mapping_assign(data=input_frames['translation'],
                                      lang=lang, id_fields=property_fields)
        if len(property_df.index) != 0:
            property_name = os.path.join(outputpath, 'property_' + name)
            property_df.to_csv(property_name, sep=';', index=False)

        print("feature mapping")
        feature_df = mapping_assign(data=input_frames['translation'],
                                    lang=lang, id_fields=feature_fields)
        if len(feature_df.index) != 0:
            feature_name = os.path.join(outputpath,'feature_' + name)
            feature_df.to_csv(feature_name, sep=';', index=False)

        text_df = text_assign(data=input_frames['translation'])
        if len(text_df.index) != 0:
            text_name = os.path.join(outputpath,'text_' + name)
            text_df.to_csv(text_name, sep=';', index=False)

        color_df = find_duplicates(color_df, 'attribute_id')
    else:
        tmb.showerror("Failed!",
                      "Input folder was not found!\nCreating a new one..")
        if(not(os.path.exists(inputpath))):
            os.makedirs(inputpath)
        if(not(os.path.exists(outputpath))):
            os.makedirs(outputpath)

    success_list = []

    if(os.path.isfile(os.path.join(outputpath, attribute_name))):
        success_list.append("attribute-file")
    if(os.path.isfile(os.path.join(outputpath, property_name))):
        success_list.append("property-file")
    if(os.path.isfile(os.path.join(outputpath, feature_name))):
        success_list.append("feature-file")
    if(os.path.isfile(os.path.join(outputpath, text_name))):
        success_list.append("text-file")

    if(len(success_list) > 0):
        tmb.showinfo("Success!", "Created {0} at\n{1}"
                     .format(",".join(success_list), outputpath))



if __name__ == '__main__':
    main()
