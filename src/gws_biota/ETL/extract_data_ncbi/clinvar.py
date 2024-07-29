# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Folder, Logger
import requests
import os
import json


class ClinVar():
    @classmethod
    def get_clinvar_data(cls, destination_dir, uids) -> Folder:
        def send_request(url, params):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error during query ({response.status_code}): {response.text}")
                return None

        uids = uids['IdList']
        Logger.info(f"Number of elements : {len(uids)}")

        # Base URL for detailed information with eutils (NCBI database API)
        for uid in uids:
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                'db': 'clinvar',
                'id': uid,
                'retmode': 'json'
            }

            # Sending the query to get detailed information
            clinvar_data = send_request(summary_url, summary_params)
            title = clinvar_data['result'][uid]['title']

            # Generate file path
            file_path = os.path.join(destination_dir, f"{title}.json")

            if clinvar_data:
                # Writing data to a JSON file
                with open(file_path, 'w', encoding="utf-8") as file:
                    json.dump(clinvar_data, file, indent=2)
            else:
                print("No detailed data found.")

        return Folder(destination_dir)
