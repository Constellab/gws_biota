

import requests

from gws_biota import ECO
from gws_biota.eco.eco_service import ECOService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text, ConfigSpecs,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("EcoDBCreator", short_description="Download the online file eco.obo (The Evidence & Conclusion Ontology) and use it to load the “biota_eco” table from the BIOTA database.")
class EcoDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"eco_file": StrParam(
        default_value="https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the ECO database...")
        DbService.drop_biota_tables([ECO])

        # ... to build it from 0
        self.log_info_message("Creating the ECO database...")
        DbService.create_biota_tables([ECO])

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("eco.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create ECO ------------- #
        # download file
        eco_file = file_downloader.download_file_if_missing(
            params["eco_file"], filename="eco.obo")

        ECOService.create_eco_db(destination_dir, eco_file)
