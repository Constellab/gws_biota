# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import ftplib
import os
import re

from Bio import Entrez
from gws_core import Folder, Logger


class GDS:
    @classmethod
    def get_geodataset(cls, destination_dir, uids) -> Folder:
        gds_ids = uids["IdList"]
        ftp_url = "ftp.ncbi.nlm.nih.gov"

        # FTP server connection
        ftp = ftplib.FTP(ftp_url)
        ftp.login()

        # Download data with Entrez (NCBI database API)
        for gds_id in gds_ids:
            handle = Entrez.efetch(db="gds", id=gds_id)
            data = handle.read()
            handle.close()

            # Regular expression to extract the FTP URL in the "data" variable
            ftp_url_pattern = r'ftp://[^\s]+'

            # Use re.search to find the first occurrence of the FTP URL
            ftp_url_match = re.search(ftp_url_pattern, data).group()
            ftp_base_dir = ftp_url_match.split("ftp://ftp.ncbi.nlm.nih.gov")[1]
            ftp.cwd(ftp_base_dir)

            local_base_dir = f"{destination_dir}/{gds_id}_downloads"

            # Stack to track directories to be processed
            stack = [(ftp_base_dir, local_base_dir)]

            while stack:
                Logger.info(f"stack : {stack}")
                remote_dir, local_dir = stack.pop()  # Removes an element from the stack for processing
                ftp.cwd(remote_dir)
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                file_list = ftp.nlst()  # Gets a list of files and subdirectories in the current FTP directory
                Logger.info(f"files : {file_list}")

                for item in file_list:
                    remote_path = os.path.join(remote_dir, item)
                    local_path = os.path.join(local_dir, item)

                    try:  # If it's a folder, cwd works and we stack
                        ftp.cwd(remote_path)
                        # adds the new directory to the stack for further processing
                        stack.append((remote_path, local_path))
                        Logger.info(f"stack append : {stack}")

                        ftp.cwd('..')

                    except ftplib.error_perm:  # Otherwise it's a file, download it
                        with open(local_path, 'wb') as f:
                            ftp.retrbinary(f"RETR {remote_path}", f.write)

        # FTP server disconnection
        ftp.quit()

        return Folder(destination_dir)
