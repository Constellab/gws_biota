

import requests

from gws_biota import BTO
from gws_biota.bto.bto_service import BTOService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, ConfigSpecs,
                      task_decorator, InputSpecs, InputSpec, OutputSpecs, OutputSpec,
                      FileDownloader, Text)

from .db_service import DbService


@task_decorator("BtoDBCreator", short_description="Download the online file bto.owl (The BRENDA Tissue Ontology) and use it to load the “biota_bto” table from the BIOTA database.")
class BtoDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, is_optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, is_optional=True)})
    config_specs = ConfigSpecs({"bto_file": StrParam(
        default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs):
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
        file_downloader = FileDownloader(
            destination_dir, message_dispatcher=self.message_dispatcher)

        # ------------- Create BTO ------------- #
        # download file
        bto_file_path = file_downloader.download_file_if_missing(
            params["bto_file"], filename="bto.owl")

        BTOService.create_bto_db(destination_dir, bto_file_path)
