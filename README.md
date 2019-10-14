Amazon Flatfile to Plentymarkets Translation Upload
---

**Dependencies**:
    python3.x

**Required**: 
    - Translations in the Amazon flatfile format saved as csv with only the last column headerline
    - Attribute Export from Plentymarkets
    - Variation Export from Plentymarkets with the variation attributes

**USE**:
    - Place the files as .csv , delimited by ';' into the Input Folder
    - Make sure that other files are removed from the folder (if the script should work automatic)
    - start script with : python3 main.py --lang {language of your choice}
        [valid values: en, fr, it, es ..]
    - Upload files using Elastic Sync
    
              
