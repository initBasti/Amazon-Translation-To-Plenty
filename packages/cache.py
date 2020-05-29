"""
    Author: Sebastian Fricke
    Date: 28.05.20
    License: GPLv3

    Implement a simple cache to store the downloaded content from the
    PlentyMarkets Exports.
"""
import urllib
import time
import bsddb3

class WebCache:
    """
        Store the data of the download in the page_database and
        the cache times in the time_database.
    """
    def __init__(self, page_database_path, time_database_path, cache_ttl):
        self.page_database = bsddb3.hashopen(page_database_path)
        self.time_database = bsddb3.hashopen(time_database_path)
        self.cache_ttl = cache_ttl

    def get_page(self, url):
        """
            Check if the content in the database is too old.
            Download new content on deprecated database content.
            Otherwise return the content from the database.

            Parameter:
                url [String] : URL of the elastic export from Plentymarkets

            Return:
                [Binary String] : Data of the File
        """
        now = time.time()
        if url in self.time_database:
            last_read = float(self.time_database[url])
            if now < last_read + float(self.cache_ttl):
                return self.page_database[url]

        str_url = url.decode()
        print(f"Download data from {str_url}..")
        starttime = time.time()
        contents = urllib.request.urlopen(str_url).read()
        endtime = time.time()
        print("Download finished [{0} us]"
              .format(round(endtime-starttime, 4)*1000000))

        self.page_database[url] = contents
        self.time_database[url] = str(now)
        self.page_database.sync()
        self.time_database.sync()

        return contents

    def dump_page(self, url):
        """
            Clean the content for a specific Export within the database

            Parameter:
                url [String] : URL of the elastic export from Plentymarkets
        """
        del self.page_database[url]
        del self.time_database[url]
        self.page_database.sync()
        self.time_database.sync()

    def clean(self):
        """
            Clear all database entries.
        """
        now = time.time()
        for (url, last_read) in self.time_database.items():
            last_read = float(last_read)
            if now >= last_read + float(self.cache_ttl):
                del self.page_database[url]
                del self.time_database[url]
        self.page_database.sync()
        self.time_database.sync()
