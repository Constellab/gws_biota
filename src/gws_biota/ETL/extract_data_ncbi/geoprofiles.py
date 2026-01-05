# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import re
import tarfile
from ftplib import FTP

import requests
from bs4 import BeautifulSoup
from gws_core import Compress, Folder, Logger


class GeoProfiles:
    @classmethod
    def get_geoprofiles_data(cls, destination_dir, uids) -> Folder:
        # Connection to FTP
        ftp = FTP("ftp.ncbi.nlm.nih.gov")
        ftp.login()

        uids = uids['IdList']
        Logger.info(f"Number of elements : {len(uids)}")

        gse_numbers = []

        for uid in uids:
            # page URL
            url = f"https://www.ncbi.nlm.nih.gov/gds?LinkName=geoprofiles_gds&from_uid={uid}"

            # Send an HTTP request to retrieve page content
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Extract HTML content from response
                html_content = response.text
            else:
                Logger.info("The request failed. Check the URL or availability of the page.")

            soup = BeautifulSoup(html_content, 'html.parser')
            html_string = soup.prettify()

            gse_number = re.findall("=(GSE[0-9]+)", html_string, re.MULTILINE)[0]
            gse_numbers.append(gse_number)

        # Loop to download .CEL files for each GSE number
        for gse_id in gse_numbers:
            series_id = gse_id[0:5]  # Extract first characters to get series ID
            url = f"/geo/series/{series_id}nnn/{gse_id}/suppl/"

            try:
                ftp.cwd(url)
            except:
                continue

            # List all files in the folder
            filenames = ftp.nlst()
            cel_files = [f for f in filenames if f.endswith('_RAW.tar')]

            # Download .CEL files
            for cel_file in cel_files:
                local_path = os.path.join(destination_dir, cel_file)
                with open(local_path, "wb") as local_file:
                    ftp.retrbinary(f"RETR {cel_file}", local_file.write)

                # Extract the content of the TAR file
                extract_path = os.path.join(destination_dir, cel_file.replace('_RAW.tar', ''))
                with tarfile.open(local_path, "r") as tar:
                    tar.extractall(path=extract_path)

                # List all files in folder and decompresses them
                for root, dirs, files in os.walk(extract_path):
                    for gz_file in files:
                        if gz_file.endswith(".gz"):
                            output_file_path = os.path.join(extract_path, gz_file)
                            Compress.smart_decompress(output_file_path, extract_path)
                            os.remove(output_file_path)

        ftp.quit()

        return Folder(destination_dir)
