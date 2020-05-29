Amazon Flatfile to Plentymarkets - Translation Upload
---

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

**Required**: 
    * Translations in the Amazon flatfile format
    * Attribute Elastic-export format at Plentymarkets as HTTP [Save the link into the Configuration]
    + ***Required Columns:***
    + AttributeValue.id
    + AttributeValueName.name
    + AttributeValue.backendName
    * Variation-Mapping Export from Plentymarkets as HTTP [Save the link into the Configuration]
    + ***Required Columns:***
    + VariationBarcode.code
    + VariationAttributeValues.attributeValues

**USE**:
    * Map the columns from the translation file to the appropriate feature/property in Plentymarkets (Example in the example_config.ini)
    * Place the translation file as .csv , delimited by ';' into the Input Folder
    * Name the file Translatin_{custom}.csv (if the script should work automatically)
    * start script with : python3 main.py --lang {language of your choice}
        [valid values: en, fr, it, es ..]
    * Upload files using Import(Elastic Sync)
