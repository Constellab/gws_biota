# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import sys
import os
import json
import requests
import re
from zipfile import ZipFile

"""
Installation script executed on server first startup
"""

def unzip(zipfile_path):
    print(f"Extracting {zipfile_path} ...")
    with ZipFile(zipfile_path, 'r') as zipObj:
        path = os.path.dirname(zipfile_path)
        zipObj.extractall(path)
    print(f"Extraction finished.")

def download(url, dest_dir, dest_filename):
        dest_zipfile_path = os.path.join(dest_dir,dest_filename)
        print(f"Downloading {url} to {dest_zipfile_path} ...")

        if os.path.exists(dest_zipfile_path):
            print(f"Data {dest_zipfile_path} already exists")
            return
        
        if dest_zipfile_path.endswith(".zip"):
            if os.path.exists(re.sub(r"\.zip$", "", dest_zipfile_path)):
                print(f"Unzipped data {dest_zipfile_path} already exists")
                return

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        with open(dest_zipfile_path, 'wb') as f:
            response = requests.get(url, stream=True)
            total = response.headers.get('content-length')

            if total is None:
                f.write(response.content)
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50*downloaded/total)
                    sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                    sys.stdout.flush()
        
        sys.stdout.write('\n')

        if dest_zipfile_path.endswith(".zip"):
            unzip(dest_zipfile_path)
            os.remove(dest_zipfile_path)

        return re.sub(r"\.zip$", "", dest_zipfile_path)

if __name__ == "__main__":
    # write content here
    _cwd_ = os.path.dirname(os.path.realpath(__file__))
    
    with open(os.path.join(_cwd_, "../settings.json")) as fp:
        _json = json.load(fp)

    # pull sqlite3db
    url = _json["urls"].get("biota:sqlite3db","")
    if url:
        dest_dir = "/prod-data/sqlite3/"         #/!\ Do not change: see settings.py
        dest_filename = "biota.sqlite3.zip"      #/!\ Do not change: see settings.py and gws.db.manager.py
        if not os.path.exists(os.path.join(dest_dir,dest_filename)):
            download(url, dest_dir, dest_filename)

    # pull mariadb
    url = _json["urls"].get("biota:mariadb","")
    if url:
        dest_dir = os.path.join(_cwd_, "")
        dest_filename = ""
        if not os.path.exists(os.path.join(dest_dir,dest_filename)):
            unzippefile_path = download(url, dest_dir, dest_filename)
            # load db
            # ...