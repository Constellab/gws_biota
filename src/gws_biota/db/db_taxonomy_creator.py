# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import requests

from gws_biota import Taxonomy
from gws_biota.taxonomy.taxonomy_service import TaxonomyService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs,
                      TaskOutputs, task_decorator, InputSpecs, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("TaxonomyDBCreator")
class TaxonomyDBCreator(Task):
    input_specs = InputSpecs({})
    output_specs = OutputSpecs({})
    config_specs = {"taxdump_files": StrParam(
        default_value="https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz")}

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the TAXONOMY database...")
        DbService.drop_biota_tables([Taxonomy])

        # ... to build it from 0
        self.log_info_message("Creating the TAXONOMY database...")
        DbService.create_biota_tables([Taxonomy])

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("taxdump.tar.gz file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create TAXONOMY ------------- #
        # download file
        taxdump_files = file_downloader.download_file_if_missing(
            params["taxdump_files"], filename="taxdump.tar.gz", decompress_file=True)

        TaxonomyService.create_taxonomy_db(destination_dir, taxdump_files)
