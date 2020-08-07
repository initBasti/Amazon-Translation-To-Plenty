# Amazon Flatfile to Plentymarkets - Translation Upload

Map the translations within your Amazon flatfile to the correct fields.  

## Getting Started

**Dependencies**:
    * python3.x
    * pandas library
    * tkinter library

### Prerequisites

1. Translations in the Amazon flatfile format

## Usage

* Map the columns from the translation file to the appropriate feature/property ID in Plentymarkets
  ('color_name'=10) 'color_name' = exact name of the columns third row in the amazon flatfile, 10 = ID of the property/Feature in Plenytmarkets
  Example:
  ```
  [PROPERTY]
  'color_name'=10
  [FEATURE]
  'size_name'=5
  ```
* Save the translation file as .csv , delimited by ';' into the any Folder
* Set a custom input / output folder with the arguments: -i / -o (As default start for the file browser)
* start script with : python3 -m translation_to_plenty --lang {language of your choice}
    [valid values: en, fr, it, es ..]
* etc   * Upload files using Import(Elastic Sync)

## Authors

* **Sebastian Fricke** - *Initial work* - [initBasti](https://github.com/initBasti)

## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details
