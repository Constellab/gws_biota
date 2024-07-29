# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (ConfigParams, OutputSpec, OutputSpecs, Task, TaskInputs, Settings,
                      task_decorator, File, StrParam, FileDownloader, Logger, FileDownloader)

import os
import requests
from ftplib import FTP
from io import BytesIO
import gzip


@task_decorator("ExtractProteomeNCBI", human_name="Download NCBI proteome file",
                short_description="Extract the proteome of an organism from NCBI")
class ExtractProteomeNCBI(Task):
    output_specs = OutputSpecs({'results': OutputSpec(File, human_name="Results",
                               short_description="Folders containing the proteome downloaded")})

    config_specs = {
        "accessionNumber": StrParam(
            human_name="Accession number", short_description="NCBI RefSeq/GenBank assembly (GCF/GCA)")}

    # --------------------- RUN ---------------------
    def run(self, params: ConfigParams, inputs: TaskInputs) -> File:
        # Retrieve the query for the request
        accession_number: str = params["accessionNumber"]
        accession_number = accession_number.replace("_", "")

        destination_dir = Settings.make_temp_dir()

        # Divide the chain into parts of length 3
        parts = [accession_number[i:i+3] for i in range(0, len(accession_number), 3)]

        ftp_path = "/".join(parts)

        # Connection to FTP
        ftp = FTP("ftp.ncbi.nlm.nih.gov")
        ftp.login()

        ftp.cwd(f"/genomes/all/{ftp_path}/")

        # List all folders in the url folder
        folder_name = ftp.nlst()

        url = f"https://ftp.ncbi.nlm.nih.gov/genomes/all/{ftp_path}/{folder_name[0]}"
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract HTML content from response
            html_content = response.text
        else:
            self.log_error_message("The request failed. Check the URL or availability of the page.")

        # List all files in the url folder
        ftp.cwd(f"/genomes/all/{ftp_path}/{folder_name[0]}")
        filenames = ftp.nlst()

        for filename in filenames:
            if filename.endswith("protein.faa.gz"):
                # Create a BytesIO object to hold the compressed data
                compressed_file = BytesIO()
                # Retrieve the compressed file and write it into the BytesIO object
                ftp.retrbinary(f"RETR {filename}", compressed_file.write)
                # Go to the start of the BytesIO object
                compressed_file.seek(0)
                # Decompress the content
                with gzip.open(compressed_file, 'rb') as decompressed_file, open("ftp_path.protein.faa", 'wb') as outfile:
                    outfile.write(decompressed_file.read())

                ftp.quit()

                return {"results": File("ftp_path.protein.faa")}
