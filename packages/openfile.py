import sys
import os
import chardet
import re
import time
from collections import OrderedDict as Odict
import csv
from tkinter import filedialog as fd
from tkinter import messagebox as tmb


class TooManyOptionsError(Exception):
    def __init__(self, message):
        super().__init__(message)


class WrongFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)


def findFile(path, amount):
    # =========================================================================
    # Initialization area
    # =========================================================================
    files = list()
    output_file = {
                    'connect': {
                                        'path': '',
                                        'encoding': ''
                                    },
                    'translation':  {
                                        'path': '',
                                        'encoding': ''
                                    },
                    'attribute':           {
                                        'path': '',
                                        'encoding': ''
                                    }
                }
    # =========================================================================
    # Use the walk function to list all files inside the output folder
    # =========================================================================
    try:
        for(dirpath, dirnames, filenames) in os.walk(path):
            files.extend(filenames)
    except Exception as err:
        print("Error @ line: {0} | Getting the files as a list!\nError: {1}\n"
              .format(sys.exc_info()[2].tb_lineno, err))

    if(len(files) == 0):
        # =====================================================================
        # No files in the folder, terminate application throw error
        # =====================================================================
        tmb.showerror("Failed!",
                      "There is no output file, in the Report folder")
        sys.exit(1)

    elif(len(files) > amount):
        # =====================================================================
        # There is more than 3 file let the user choose a file
        # =====================================================================
        print("more files than amount")
        for index, opt in enumerate([*output_file]):
            output_file[opt]['path'] = fd.askopenfilename(title="{0} file"
                                                          .format(opt),
                                                          initialdir=path)

    elif(len(files) == amount):
        # =====================================================================
        # There are only 3 file, check if the files are csv
        # and check for the names: translation, id, connect
        # =====================================================================
        for opt in [*output_file]:
            for i in range(amount):
                try:
                    if(re.search(r'\b%s_\w+.csv\b' % opt, files[i])):
                        output_file[opt]['path'] = os.path.join(path,
                                                                files[i])
                    elif(re.match(r'\b{0}-\w+.csv\b'.format(opt), files[i])):
                        output_file[opt]['path'] = os.path.join(path,
                                                                files[i])
                    elif(re.match(r'\b{0}\w+.csv\b'.format(opt), files[i])):
                        output_file[opt]['path'] = os.path.join(path,
                                                                files[i])

                except Exception as err:
                    print("Error @ line: {0} | Checking .csv and name\n{1}\n"
                          .format(sys.exc_info()[2].tb_lineno, err))

    for index, opt in enumerate([*output_file]):
        if(not(output_file[opt]['path'])):
            # =================================================================
            # import OrderedDict as Odict If there is still no path
            # decleared let the user choose
            # =================================================================
            output_file[opt]['path'] = fd.askopenfilename(title="{0} file!"
                                                          .format(opt),
                                                          initialdir=path)

    output_file = checkEncoding(data=output_file)

    return output_file


def openFiles(files):
    Data = Odict()
    column_names = ['variation',
                    'color_value',
                    'color_value_translation',
                    'color_id',
                    'color_backend',
                    'size_value',
                    'size_value_translation',
                    'size_id',
                    'size_backend',
                    'found_color',
                    'found_size']

    for index, f in enumerate([*files]):
        with open(files[f]['path'], 'r', encoding=files[f]['encoding']) as i:
            reader = csv.DictReader(i, delimiter=";")

            starttime = time.time()
            for row in reader:
                if(index == 0):
                    try:
                        # color-connect file
                        color = ''
                        size = ''
                        attr = row['VariationAttributeValues.attributeValues']
                        found_color = False
                        found_size = False
                        if(row['Variation.isMain'] == 1):
                            break

                        variation = row['Variation.number']
                        color = parseColorValue(attr)
                        # size = parseSizeValue(attr)

                        if(color):
                            found_color = True
                        if(size):
                            found_size = True

                        values = [variation,
                                  color, '', '',
                                  size, '', '',
                                  found_color, found_size]

                        Data[variation] = Odict(zip(column_names, values))
                    except Exception as err:
                        print("Error @ line(openFile): {0} connect\n{1}\n"
                              .format(sys.exc_info()[2].tb_lineno, err))

                elif(index == 1):
                    # translation file
                    try:
                        for d in Data:
                            c_t = ''
                            s_t = ''
                            if(Data[d]['found_color']):
                                c_t = ColorTranslateValue(Data[d]['variation'],
                                                          row)
                            # if(Data[d]['found_size']):
                            # s_t = SizeTranslateValue(Data[d]['variation'],
                                #                             row)

                            if(c_t):
                                Data[d]['color_value_translation'] = c_t
                            if(s_t):
                                Data[d]['size_value_translation'] = s_t
                    except Exception as err:
                        print("Error @ line(openFile): {0} translation\n{1}\n"
                              .format(sys.exc_info()[2].tb_lineno, err))

                elif(index == 2):
                    # id file
                    try:
                        for d in Data:
                            c_data = dict()
                            s_data = dict()
                            if(Data[d]['found_color'] and
                               Data[d]['color_value_translation']):
                                c_data = findIdForValue(Data[d]['color_value'],
                                                      row=row)
                            if(Data[d]['found_size'] and
                               Data[d]['size_value_translation']):
                                s_data = findIdForValue(Data[d]['size_value'],
                                                      row=row)
                            if(c_data):
                                Data[d]['color_id'] = c_data['id']
                                Data[d]['color_backend'] = c_data['backend']
                            if(s_data):
                                Data[d]['size_id'] = s_data['id']
                                Data[d]['size_backend'] = s_data['backend']
                    except Exception as err:
                        print("Error @ line(openFile): {0} id\n{1}\n"
                              .format(sys.exc_info()[2].tb_lineno, err))

            endtime = time.time()
            print("file[{0}] execution time: {1}us"
                  .format(index, round((endtime-starttime)*1000000, 4)))
    return Data


def checkEncoding(data):
    raw_data = ''
    for index, opt in enumerate([*data]):
        try:
            # =================================================================
            # Check the encoding of the path
            # =================================================================
            with open(data[opt]['path'], mode='rb') as item:
                raw_data = item.read(50000)
            data[opt]['encoding'] = chardet.detect(raw_data)['encoding']
        except Exception as err:
            print("Error @ line: {0} | Error at encode check\nError: {1}|{2}\n"
                  .format(sys.exc_info()[2].tb_lineno, err,
                          data[opt]['path']))

        if(not(data[opt]['encoding'])):
            # =================================================================
            # If there is no encoding assigned assume it to be utf-8
            # =================================================================
            data[opt]['encoding'] = 'utf-8'

    return data


def parseColorValue(line):
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

    return None


def parseSizeValue(line):
    full_option = 0
    line_list = []
    if(not(line)):
        return None
    if(re.search(r'size_name', line)):
        if(re.search(r'color', line) and re.search(r',', line)):
            line_list = line.split(',')
        else:
            if(re.search(r':', line) and not(re.search(r',', line))):
                return line.split(':')[1]

        if(len(line_list) > 2):
            for i in range(len(line_list)):
                if(not(re.search(r':', line_list[i]))):
                    # in case the value contains a ','
                    new_value = ','.join(line_list[i-1:i])
                    if(re.search(r'size', new_value)):
                        return new_value.split(':')[1]
                else:
                    full_option = full_option + 1
                if(full_option > 2):
                    raise TooManyOptionsError('Too many Options:{0}'
                                              .format(line))
        elif(len(line_list) == 2):
            for i in range(2):
                if(re.search(r'size_name', line_list[i])):
                    return line_list[i].split(':')[1]
    elif(not(re.search(r'size_name', line))):
        return None

    return None


def findIdForValue(value, row):
    attr_data = Odict()
    columns = {'id': '', 'backend': ''}

    if('AttributeValue.id' in [*row] and
       'AttributeValueName.name' in [*row] and
       'AttributeValue.backendName' in [*row]):
        if(re.fullmatch(value, row['AttributeValue.backendName'])
           or re.fullmatch(value, row['AttributeValueName.name'])):
            values = [row['AttributeValue.id'],
                      row['AttributeValue.backendName']]
            attr_data[value] = Odict(zip(columns, values))
            return attr_data[value]
        else:
            values = [None, None]
            attr_data[value] = Odict(zip(columns, values))
            return attr_data[value]
    else:
        raise WrongFormatError('The file has the wrong header')

    return None


def ColorTranslateValue(variation, row):
    if('item_sku' in [*row] and 'color_name' in [*row]):
        if(re.match(variation, row['item_sku'], re.IGNORECASE)):
            return row['color_name']
        else:
            return None
    else:
        raise WrongFormatError('The file has the wrong header')

    return None


def SizeTranslateValue(variation, row):
    if('item_sku' in [*row] and 'size_name' in [*row]):
        if(re.match(variation, row['item_sku'], re.IGNORECASE)):
            return row['size_name']
        else:
            return None
    else:
        raise WrongFormatError('The file has the wrong header:{0}'
                               .format([*row]))

    return None


def property_assign(files, lang):
    id_fields = {
        '7': 'outer_material_type',
        '8': 'material_composition',
        '13': 'department_name',
        '15': 'bullet_point1',
        '16': 'bullet_point2',
        '17': 'bullet_point3',
        '24': 'bullet_point4',
        '19': 'bullet_point5',
        '21': 'style_name',
        '26': 'neck_size',
        '28': 'pattern_type',
        '29': 'sleeve_type'
    }

    Data = Odict()
    num = 0

    column_names = ['sku', 'id', 'value', 'lang']
    with open(files['path'], 'r', encoding=files['encoding']) as i:
        reader = csv.DictReader(i, delimiter=";")

        starttime = time.time()
        for row in reader:
            id_value = 0
            sku = row['item_sku']
            value = ''
            if(not(row['parent_child'] == 'child')):
                try:
                    for i, field in enumerate(id_fields):
                        if(id_fields[field] in [*row]):
                            if(row[id_fields[field]]):
                                id_value = field
                                value = row[id_fields[field]]
                                values = [sku, id_value, value, lang]

                                Data[sku+'_'+field+'_'+str(num)] = \
                                    Odict(zip(column_names,
                                              values))
                                num = num+1
                except Exception as err:
                    print("Error @ property_assign line: {0}find fields\n{1}\n"
                          .format(sys.exc_info()[2].tb_lineno, err))
        endtime = time.time()
        print("property find execution time: {0}us"
              .format(round(endtime-starttime)*1000000, 4))

    return Data


def feature_assign(files, lang):
    id_fields = {
        '1': 'color_map',
        '8': 'sleeve_type',
        '11': 'pattern_type',
        '12': 'collar_style',
        '13': 'item_name',
        '14': 'closure_type',
        '15': 'style_name',
        '16': 'care_instructions'
    }

    Data = Odict()

    column_names = ['sku', 'id', 'value', 'lang']
    with open(files['path'], 'r', encoding=files['encoding']) as i:
        reader = csv.DictReader(i, delimiter=";")

        starttime = time.time()
        for row in reader:
            id_value = 0
            sku = row['item_sku']
            value = ''
            try:
                for i, field in enumerate(id_fields):
                    if(id_fields[field] in [*row]):
                        if(row[id_fields[field]]):
                            id_value = field
                            value = row[id_fields[field]]
                            values = [sku, id_value, value, lang]

                            if(not(row['parent_child'] == 'parent')):
                                Data[sku+'_'+field] = Odict(zip(column_names,
                                                                values))
            except Exception as err:
                print("Error @ feature_assign line: {0}find fields\n{1}\n"
                      .format(sys.exc_info()[2].tb_lineno, err))
        endtime = time.time()
        print("feature find execution time: {0}us"
              .format(round(endtime-starttime)*1000000, 4))

    return Data


def text_assign(files):
    Data = Odict()
    num = 0

    column_names = ['sku', 'description', 'keywords']
    with open(files['path'], 'r', encoding=files['encoding']) as i:
        reader = csv.DictReader(i, delimiter=";")

        starttime = time.time()
        for row in reader:
            sku = row['item_sku']
            desc = row['product_description']
            keys = row['generic_keywords']
            try:
                if(not(row['parent_child'] == 'child')):
                    values = [sku, desc, keys]

                    Data[sku+"_"+str(num)] = Odict(zip(column_names, values))
                    num = num+1
            except Exception as err:
                print("Error @ text_assign line: {0}find fields\n{0}|{1}\n"
                      .format(sys.exc_info()[2].tb_lineno, err))
        endtime = time.time()
        print("text find execution time: {0}us"
              .format(round(endtime-starttime)*1000000, 4))

    return Data


def find_duplicates(target):
    color_set = set()
    id_set = set()
    translation_set = set()
    remove = set()

    for row in target:
        color = target[row]['color_value']
        id_value = target[row]['color_id']
        translation = target[row]['color_value_translation']
        if(color in color_set):
            remove.add(row)
        else:
            color_set.add(color)

        if(id_value in id_set):
            remove.add(row)
        else:
            id_set.add(id_value)

        if(translation in translation_set):
            remove.add(row)
        else:
            translation_set.add(translation)

    copy = dict(target)
    for i in remove:
        del copy[i]

    return copy
