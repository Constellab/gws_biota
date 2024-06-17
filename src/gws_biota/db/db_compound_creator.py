

import requests

from gws_biota import Compound
from gws_biota.compound.compound_service import CompoundService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("CompoundDBCreator")
class CompoundDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, is_optional=True)})
    output_specs = OutputSpecs({"output_text": OutputSpec(Text, is_optional=True)})

    config_specs = {"compound_file": StrParam(
        default_value="https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo")}

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the CHEBI database...")
        DbService.drop_biota_tables([Compound])

        # ... to build it from 0
        self.log_info_message("Creating the CHEBI database...")
        DbService.create_biota_tables([Compound])

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("chebi.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create COMPOUND ------------- #
        # download file
        compound_file_path = file_downloader.download_file_if_missing(
            params["compound_file"], filename="chebi.obo")

        CompoundService.create_compound_db(destination_dir, compound_file_path)
