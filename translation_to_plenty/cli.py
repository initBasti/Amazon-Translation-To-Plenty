"""
    Author: Sebastian Fricke
    Date: 29.05.20
    License: GPLv3

    Create upload files for the PlentyMarkets import (Elastic Sync) with
    translations stored inside of a Amazon Flatfile (csv).

    Pull required mapping information from Plentymarkets and store mapping
    IDs for properties and features inside of the configuration.
"""

import os
import sys
import datetime
import tkinter
import argparse
import configparser
from tkinter import messagebox as tmb
from tkinter import filedialog as fd
import pandas
import chardet
from translation_to_plenty.packages.assignment import (
    mapping_assign, text_assign)

USER = os.getlogin()
if sys.platform == 'linux':
    CONFIG_FILE = os.path.join('/', 'home', str(f'{USER}'),
                               '.translation_to_plenty_config.ini')
elif sys.platform == 'win32':
    CONFIG_FILE = os.path.join('C:', 'Users', str(f'{USER}'),
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
    parser.add_argument('-l', '--lang', action='store',
                        choices=['en', 'fr', 'it', 'es'], required=True,
                        dest='lang')
    parser.add_argument('--custom-input-folder', '-i', action='store_true',
                        dest='input_path')
    parser.add_argument('--custom-output-folder', '-o', action='store_true',
                        dest='output_path')
    return parser.parse_args()

def cli():
    inputpath = ''
    outputpath = ''
    inputfile = {'path':'', 'encoding':''}

    root = tkinter.Tk()
    root.withdraw()

    args = initialize_argument_parser()

    if args.input_path:
        custom_input_path = fd.askdirectory(title='custom input file folder')

    if args.output_path:
        custom_output_path = fd.askdirectory(title='custom output file folder')

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if not config.sections():
        print(f"{CONFIG_FILE} required")
        sys.exit(1)

    if args.input_path:
        if os.path.exists(args.input_path):
            config['GENERAL']['custom_input_folder'] = custom_input_path

    if args.output_path:
        if os.path.exists(args.output_path):
            config['GENERAL']['custom_output_folder'] = custom_output_path

    if args.input_path or args.output_path:
        with open(CONFIG_FILE, mode='w') as configfile:
            config.write(configfile)

    if config['GENERAL']['custom_input_folder']:
        inputpath = config['GENERAL']['custom_input_folder']

    if config['GENERAL']['custom_output_folder']:
        outputpath = config['GENERAL']['custom_output_folder']

    if inputpath:
        inputfile['path'] = fd.askopenfilename(title="Translation file",
                                       initialdir=inputpath)
    else:
        inputfile['path'] = fd.askopenfilename(title="Translation file")
    inputfile = check_encoding(data=inputfile)

    input_frame = read_data(data=inputfile)
    if len(input_frame.index) == 0:
        sys.exit(1)

    if os.path.exists(outputpath):
        create_upload_file(data=input_frame, name='property',
                           path=outputpath, lang=args.lang,
                           id_fields=config['PROPERTY'])
        create_upload_file(data=input_frame, name='feature',
                           path=outputpath, lang=args.lang,
                           id_fields=config['FEATURE'])
        create_upload_file(data=input_frame, name='text',
                           path=outputpath, lang=args.lang)

    else:
        tmb.showerror("Failed!",
                      "folders were not found!\nCreating new ones..")
        if not os.path.exists(inputpath):
            os.makedirs(inputpath)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)
