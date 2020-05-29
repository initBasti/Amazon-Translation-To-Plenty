# Amazon Flatfile to Plentymarkets - Translation Upload

Map the translations within your Amazon flatfile to the correct fields.  

## Getting Started

**Dependencies**:
    * python3.x
    * pandas library
    * numpy library
    * argparse library
    * configparse library
    * tkinter library
    * chardet library
    * urllib library
    * bsddb3 library

### Prerequisites

1. Translations in the Amazon flatfile format
2. Attribute Elastic-export format at Plentymarkets as HTTP [Save the link into the Configuration]
    * ***Required Columns:***
        - AttributeValue.id
        - AttributeValueName.name
        - AttributeValue.backendName
3. Variation-Mapping Export from Plentymarkets as HTTP [Save the link into the Configuration]
    * ***Required Columns:***
        - VariationBarcode.code
        - VariationAttributeValues.attributeValues

## Usage

* Map the columns from the translation file to the appropriate feature/property in Plentymarkets (Example in the example_config.ini)
* Place the translation file as .csv , delimited by ';' into the Input Folder
* Name the file Translatin_{custom}.csv (if the script should work automatically)
* start script with : python3 main.py --lang {language of your choice}
    [valid values: en, fr, it, es ..]
* etc   * Upload files using Import(Elastic Sync)

## Authors

* **Sebastian Fricke** - *Initial work* - [initBasti](https://github.com/initBasti)

## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details
