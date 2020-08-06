"""
    Author: Sebastian Fricke
    Date: 29.05.20
    License: GPLv3

    Create upload files for the PlentyMarkets import (Elastic Sync) with
    translations stored inside of a Amazon Flatfile (csv).

    Pull required mapping information from Plentymarkets and store mapping
    IDs for properties and features inside of the configuration.
"""

import re
import platform
import os
import sys
import datetime
import tkinter
import argparse
import configparser
from io import StringIO
from tkinter import messagebox as tmb
from tkinter import filedialog as fd
import pandas
import chardet
from packages.assignment import (
    mapping_assign, text_assign)

if sys.platform == 'linux':
    linux_user = os.getlogin()
    CONFIG_FILE = os.path.join('/', 'home', str(f'{linux_user}'),
                               '.translation_to_plenty_config.ini')
elif sys.platform == 'win32':
    win_user = os.getlogin()
    CONFIG_FILE = os.path.join('C:', 'Users', str(f'{win_user}'),
                               '.translation_to_plenty_config.ini')

def read_data(data):
    """
        Read the data from the translation file into a pandas Dataframe.
        Check if they contain the required columns.
        Skip unnecessary columns for files in the amazon flatfile format.

        Parameter:
            data [Dict] : Dictionary with paths/content of the input file

        Return:
            [DataFrame]
    """
    frame = pandas.read_csv(data['path'], sep=';')
    if not 'item_sku' in frame.columns:
        frame = pandas.read_csv(data['path'], sep=';',
                                header=2)
        if not 'item_sku' in frame.columns:
            print("ERROR: Input file has to be a Amazon flatfile")
            return None

    return frame

def find_file(path):
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
    for walk_result in os.walk(path):
        files.extend(walk_result[2])

    if len(files) == 0:
        tmb.showerror("No input error!",
                      "There is no input file, in the Input folder")
        sys.exit(1)

    for item in files:
        if re.search(r'\btranslation_\w+.csv\b', item):
            outputfile = os.path.join(path, item)
    if not outputfile:
        outputfile = fd.askopenfilename(title="Translation file",
                                        initialdir=path)

    return outputfile

def check_encoding(data):
    """
        Assume the encoding of the binary raw data of an input file.

        Parameter:
            data [Dict] : Dictionary object with the path of the file

        Return:
            data [Dict] : Dictionary with encoding mapping
    """
    raw_data = ''
    with open(data['path'], mode='rb') as item:
        raw_data = item.read(50000)
    data['encoding'] = chardet.detect(raw_data)['encoding']

    if not data['encoding']:
        data['encoding'] = 'utf-8'

    return data

def build_path_name(base_path, name, lang):
    """
        Create a path name for a new file with the current date, the
        language of the translation and .csv as file type.

        Parameter:
            base_path [String] : Path of the project's Output folder
            name [String] : Name of the specific file

        Return:
            [OS.path] : OS independent path to the new file
    """
    todaystr = datetime.datetime.now().strftime("%d-%m-%Y")
    addition = '_' + lang + '_' + todaystr + '.csv'
    return os.path.join(base_path, name + addition)

def create_upload_file(data, name, path, lang, id_fields=''):
    """
        Wrapper around the assignment function for the different types:
            attribute, property, feature and text

        Parameter:
            data [DataFrame]
            name [String]       : Start of the name of the file
            path [String]       : File path of the 'Output' folder
            lang [String]       : CLI argument of the chosen language
            id_fields [Dict]    : Mapping of Plentymarkets ID to Amazon
                                  Flatfile column name
    """
    print(f"{name} mapping:")
    if name in ('property', 'feature'):
        frame = mapping_assign(data=data, lang=lang, id_fields=id_fields)
    elif name == 'text':
        frame = text_assign(data=data)
    if len(frame.index) != 0:
        write_path = build_path_name(base_path=path, name=name, lang=lang)
        frame.to_csv(write_path, sep=';', index=False)
        print(f"Data saved successfully under {write_path}.")

def initialize_argument_parser():
    """
        Setup the different command-line argument options.

        Return:
            [Namespace] parsed arguments as namespace
    """
    parser = argparse.ArgumentParser(description='lang value')
    parser.add_argument('--l', '--lang', action='store',
                        choices=['en', 'fr', 'it', 'es'], required=True)
    return parser.parse_args()

def main():
    inputpath = ''
    outputpath = ''
    inputfile = {'path':'', 'encoding':''}
    lang = ''

    root = tkinter.Tk()
    root.withdraw()

    args = initialize_argument_parser()
    lang = args.l

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if not config.sections():
        print(f"{CONFIG_FILE} required")
        sys.exit(1)

    if platform.system() == 'Linux':
        inputpath = os.path.join(os.getcwd(), 'Input')
        outputpath = os.path.join(os.getcwd(), 'Output')

    else:
        inputpath = os.path.join(os.path.join(os.getcwd(), os.pardir),
                                 'Input')
        outputpath = os.path.join(os.path.join(os.getcwd(), os.pardir),
                                  'Output')

    if os.path.exists(inputpath):
        inputfile['path'] = find_file(path=inputpath)
    print(inputfile)
    inputfile = check_encoding(data=inputfile)

    input_frame = read_data(data=inputfile)
    if len(input_frame.index) == 0:
        sys.exit(1)

    if os.path.exists(outputpath):
        create_upload_file(data=input_frame, name='property',
                           path=outputpath, lang=lang,
                           id_fields=config['PROPERTY'])
        create_upload_file(data=input_frame, name='feature',
                           path=outputpath, lang=lang,
                           id_fields=config['FEATURE'])
        create_upload_file(data=input_frame, name='text',
                           path=outputpath, lang=lang)

    else:
        tmb.showerror("Failed!",
                      "folders were not found!\nCreating new ones..")
        if not os.path.exists(inputpath):
            os.makedirs(inputpath)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

if __name__ == '__main__':
    main()
