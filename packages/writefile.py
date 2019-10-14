import csv
import sys
import os


def writeFile(dataset, filename, fieldnames, folder):
    upload_path = ''

    try:
        upload_path = os.path.join(folder, filename)
    except Exception as err:
        print("Error @ line: {0} | Creating Upload path\nError : {1}\n"
              .format(sys.exc_info()[2].tb_lineno, err))

    with open(upload_path, mode='w') as item:
        writer = csv.DictWriter(item, delimiter=';',
                                fieldnames=fieldnames,
                                lineterminator='\n')

        writer.writeheader()
        for row in dataset:
            try:
                writer.writerow(dataset[row])
            except Exception as err:
                print("Error @ line: {0} | Writing a row\nError : {1}\n"
                      .format(sys.exc_info()[2].tb_lineno, err))

    if(os.path.exists(upload_path)):
        return upload_path
    else:
        return None
