import platform
import os
from collections import OrderedDict as Odict
import sys
import datetime
import tkinter
import argparse
import configparser
from tkinter import messagebox as tmb
from packages.openfile import (
    findFile, openFiles, property_assign, feature_assign,
    text_assign, find_duplicates, checkEncoding)
from packages.writefile import writeFile


def main():
    # =========================================================================
    # Initilization Area
    # =========================================================================
    Data = Odict()
    x_Data = {'property': Odict(), 'feature': Odict(), 'text': Odict()}
    inputpath = ''
    outputpath = ''
    inputfiles = {
        'attribute':{'path':'', 'encoding':''},
        'translation':{'path':'', 'encoding':''},
        'connect':{'path':'', 'encoding':''}}
    outputfile = ''
    propertyfile = ''
    featurefile = ''
    textfile = ''
    todaystr = ''
    name = ''
    lang = ''

    attribute_data = Odict()

    root = tkinter.Tk()
    root.withdraw()

    # =========================================================================
    # Getting command line arguments
    # =========================================================================
    parser = argparse.ArgumentParser(description='lang value')
    parser.add_argument('--l', '--lang', action='store',
                        choices=['en', 'fr', 'it', 'es'])
    args = parser.parse_args()
    lang = args.l
    if(lang):
        lang = lang.upper()
    else:
        lang = 'default'.upper()

    # =========================================================================
    # Read the URL of the elasitc export formats for the attribute values
    # and the variation-attribute mapping
    # =========================================================================
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not config.sections():
        print(f"config.ini required\n{err}")
        exit(1)


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

    if(os.path.exists(inputpath)):
        try:
            Data = openFiles(files=inputfiles)
        except Exception as err:
            print("Error @ line : {0} opening files\nError: {1}\n"
                  .format(sys.exc_info()[2].tb_lineno, err))

        for i in [*x_Data]:
            if(lang == 'DEFAULT'):
                print("WARNING: No language assigned, adjust file!")
            if i == 'property':
                x_Data[i] = property_assign(files=inputfiles['translation'],
                                            lang=lang)
            elif i == 'feature':
                x_Data[i] = feature_assign(files=inputfiles['translation'],
                                           lang=lang)
            elif i == 'text':
                x_Data[i] = text_assign(files=inputfiles['translation'])

        # =================================================================
        # create the upload format, remove duplicates
        # =================================================================
        Data = find_duplicates(Data)
        column_names = ['value-name', 'value-id', 'value-backend']
        for row in Data:
            if(Data[row]['color_value_translation']):
                values = [Data[row]['color_value_translation'],
                          Data[row]['color_id'], Data[row]['color_backend']]
                attribute_data[row + '_color'] = Odict(zip(column_names,
                                                           values))

        # =================================================================
        # Write the dataset to a new file in the upload folder
        # The name should contain the date
        # =================================================================
        if(os.path.exists(outputpath)):
            try:
                todaystr = datetime.datetime.now().strftime("%d-%m-%Y")
                name = lang + '_' + todaystr + '.csv'
            except Exception as err:
                print("Error @ line : {0} date and filename\n{1}\n"
                      .format(sys.exc_info()[2].tb_lineno, err))
            try:
                outputfile = writeFile(dataset=attribute_data,
                                       filename='attribute_' + name,
                                       folder=outputpath,
                                       fieldnames=column_names)
            except Exception as err:
                print("Error @ line : {0} Writing the file\nError: {1}\n"
                      .format(sys.exc_info()[2].tb_lineno, err))
                tmb.showerror("Failed!",
                              "Error at writing the new file\n")

            for i in [*x_Data]:
                try:
                    if i == 'property':
                        f_name = [*x_Data['property'][[*x_Data['property']][0]]]
                        propertyfile = writeFile(dataset=x_Data['property'],
                                                 filename='property_' + name,
                                                 folder=outputpath,
                                                 fieldnames=f_name)
                    elif i == 'feature':
                        f_name = [*x_Data['feature'][[*x_Data['feature']][0]]]
                        featurefile = writeFile(dataset=x_Data['feature'],
                                                filename='feature_' + name,
                                                folder=outputpath,
                                                fieldnames=f_name)
                    elif i == 'text':
                        f_name = [*x_Data['text'][[*x_Data['text']][0]]]
                        textfile = writeFile(dataset=x_Data['text'],
                                             filename='text_' + name,
                                             folder=outputpath,
                                             fieldnames=f_name)
                except Exception as err:
                    print("Error @ line : {0} Writing the {2} file\nError: {1}\n"
                          .format(sys.exc_info()[2].tb_lineno, err, i))
                    tmb.showerror("Failed!",
                                  "Error at writing the new {0} file\n"
                                  .format(i))

        else:
            # =============================================================
            # If there is no Outputpath throw error and create a
            # new set of folders
            # =============================================================
            tmb.showerror("Failed!",
                          "Output folder was not found!\n")
            os.makedirs(outputpath)
            if(not(os.path.exists(inputpath))):
                os.makedirs(inputpath)
        success_list = []

        if(os.path.isfile(outputfile)):
            success_list.append("attribute-file")
        if(os.path.isfile(propertyfile)):
            success_list.append("property-file")
        if(os.path.isfile(featurefile)):
            success_list.append("feature-file")
            tmb.showinfo("Success!", "Finished file created at:\n{0}"
                         .format(featurefile))
        if(os.path.isfile(textfile)):
            success_list.append("text-file")

        if(len(success_list) > 0):
            tmb.showinfo("Success!", "Created {0} at\n{1}"
                         .format(",".join(success_list),
                                 outputpath))

    else:
        # =====================================================================
        # If there is no Inputpath throw error and create a new set of folders
        # =====================================================================
        tmb.showerror("Failed!",
                      "Input folder was not found!\nCreating a new one..")
        os.makedirs(inputpath)
        if(not(os.path.exists(outputpath))):
            os.makedirs(outputpath)


if __name__ == '__main__':
    main()
