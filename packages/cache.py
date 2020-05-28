import bsddb3
import urllib
import requests
import time

class WebCache:
    def __init__(self, page_database_path, time_database_path, cache_ttl):
        self.page_database = bsddb3.hashopen(page_database_path)
        self.time_database = bsddb3.hashopen(time_database_path)
        self.cache_ttl = cache_ttl

    def get_page(self, url):
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
        del self.page_database[url]
        del self.time_database[url]
        self.page_database.sync()
        self.time_database.sync()

    def clean(self):
        now = time.time()
        for (url, last_read) in self.time_database.items():
            last_read = float(last_read)
            if now >= last_read + float(self.cache_ttl):
                del self.page_database[url]
                del self.time_database[url]
        self.page_database.sync()
        self.time_database.sync()
