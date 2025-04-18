

import requests

from gws_biota import Protein
from gws_biota.protein.protein_service import ProteinService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text, ConfigSpecs,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("ProteinDBCreator",
                short_description="Download the online file uniprot_sprot.fasta.gz from uniprot database and use it to load the “biota_protein” table from the BIOTA database.")
class ProteinDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, is_optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, is_optional=True)})
    config_specs = ConfigSpecs({"protein_file": StrParam(
        default_value="https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the PROTEIN database...")
        DbService.drop_biota_tables([Protein])

        # ... to build it from 0
        self.log_info_message("Creating the PPROTEIN database...")
        DbService.create_biota_tables([Protein])

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("uniprot_sprot.fasta.gz file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create PROTEIN ------------- #
        # download file
        protein_file = file_downloader.download_file_if_missing(
            params["protein_file"], filename="uniprot_sprot.fasta.gz")

        ProteinService.create_protein_db(destination_dir, protein_file)
