

import requests

from gws_biota import SBO
from gws_biota.sbo.sbo_service import SBOService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text, ConfigSpecs,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("SboDBCreator", short_description="Download the online file SBO_OBO.obo (Systems Biology Ontology) and use it to load the “biota_sbo” table from the BIOTA database.")
class SboDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"sbo_file": StrParam(
        default_value="https://raw.githubusercontent.com/EBI-BioModels/SBO/2143b2973f8912db9d4324a4fe543aabcd8f8ba7/SBO_OBO.obo")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the SBO database...")
        DbService.drop_biota_tables([SBO])

        # ... to build it from 0
        self.log_info_message("Deleting the SBO database...")
        DbService.create_biota_tables([SBO])

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("sbo.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create SBO ------------- #
        # download file
        sbo_file = file_downloader.download_file_if_missing(
            params["sbo_file"], filename="sbo.obo")

        SBOService.create_sbo_db(destination_dir, sbo_file)
