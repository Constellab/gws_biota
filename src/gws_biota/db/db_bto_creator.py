# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import requests

from gws_biota import BTO
from gws_biota.bto.bto_service import BTOService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs,
                      TaskOutputs, task_decorator, InputSpecs, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("BtoDBCreator")
class BtoDBCreator(Task):
    input_specs = InputSpecs({})
    output_specs = OutputSpecs({})
    config_specs = {"bto_file": StrParam(
        default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl")}

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the BTO database...")
        DbService.drop_biota_tables([BTO])

        # ... to build it from 0
        self.log_info_message("Creating the BTO database...")
        DbService.create_biota_tables([BTO])

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("bto.owl file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create BTO ------------- #
        # download file
        bto_file = file_downloader.download_file_if_missing(
            params["bto_file"], filename="bto.owl")

        BTOService.create_bto_db(destination_dir, bto_file)
