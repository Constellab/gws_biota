

import requests

from gws_biota import Pathway
from gws_biota.pathway.pathway_service import PathwayService

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader)

from .db_service import DbService


@task_decorator("PathwayDBCreator", short_description="Download the online files from rgd.mcw.edu and reactome databases and use them to load the “biota_pathway” table from the BIOTA database.")
class PathwayDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, is_optional=True)})
    output_specs = OutputSpecs({"output_text": OutputSpec(Text, is_optional=True)})
    config_specs = {"pwo_file": StrParam(
        default_value="https://download.rgd.mcw.edu/ontology/pathway/pathway.obo"),
        "reactome_pathways_file": StrParam(default_value="https://reactome.org/download/current/ReactomePathways.txt"),
        "reactome_pathway_relations_file": StrParam(default_value="https://reactome.org/download/current/ReactomePathwaysRelation.txt"),
        "reactome_chebi_pathways_file": StrParam(default_value="https://reactome.org/download/current/ChEBI2Reactome.txt")}

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the PATHWAY database...")
        DbService.drop_biota_tables([Pathway])

        # ... to build it from 0
        self.log_info_message("Creating the PATHWAY database...")
        DbService.create_biota_tables([Pathway])

        # Check that all url exist and work
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("All files were found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create PATHWAY ------------- #
        # download pathway file
        pathway_file = file_downloader.download_file_if_missing(
            params["pwo_file"], filename="pathway.obo")

        # download reactome pathway file
        reactome_pathways_file = file_downloader.download_file_if_missing(
            params["reactome_pathways_file"], filename="ReactomePathways.txt")

        # download reactome pathway relation file
        reactome_pathway_relations_file = file_downloader.download_file_if_missing(
            params["reactome_pathway_relations_file"], filename="ReactomePathwaysRelation.txt")

        # download reactome chebi pathway file
        reactome_chebi_pathways_file = file_downloader.download_file_if_missing(
            params["reactome_chebi_pathways_file"], filename="ChEBI2Reactome.txt")

        PathwayService.create_pathway_db(
            destination_dir, pathway_file, reactome_pathways_file, reactome_pathway_relations_file,
            reactome_chebi_pathways_file)
