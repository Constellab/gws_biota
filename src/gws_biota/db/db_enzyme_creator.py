

import os
import requests

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader, File)

from gws_biota import Enzyme
from gws_biota.enzyme.enzyme_service import EnzymeService
from ..bto.bto import BTO
from ..taxonomy.taxonomy import Taxonomy
from ..pathway.pathway import Pathway
from .db_service import DbService


@task_decorator("EnzymeDBCreator", short_description="Download the online folders/files from BRENDA, ebi.ac.uk and ncbi databases and use them to load the “biota_enzyme” table from the BIOTA database.")
class EnzymeDBCreator(Task):
    input_specs = InputSpecs({'input_brenda': InputSpec(File, human_name="Enzyme file",
                             short_description="Enzyme file from BRENDA database"),
                             "input_bto": InputSpec(Text, human_name="link to bto", is_optional=True),
                              "input_taxonomy": InputSpec(Text, human_name="link to taxonomy", is_optional=True),
                              "input_protein": InputSpec(Text, human_name="link to protein", is_optional=True)})

    output_specs = OutputSpecs({"output_text": OutputSpec(Text, is_optional=True)})
    config_specs = {"bkms_file": StrParam(default_value="https://bkms.brenda-enzymes.org/download/Reactions_BKMS.tar.gz"), "expasy_file": StrParam(
        default_value="https://raw.githubusercontent.com/google-research/proteinfer/540773f988005cc5ed834210d1477e4db1f141e6/testdata/enzclass.txt"),
        "compound_file": StrParam(default_value="https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo"),
        "bto_file": StrParam(default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl"),
        "taxdump_files": StrParam(default_value="https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz")}

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        input_file: File = inputs["input_brenda"]

        len_bto = BTO.select().count()
        len_taxonomy = Taxonomy.select().count()
        len_pathway = Pathway.select().count()

        # Check that dependent databases are available before downloading enzyme data.
        if len_bto == 0 or len_taxonomy == 0 or len_pathway == 0:
            raise Exception(
                "No data from the TAXONOMY, BTO or PATHWAY databases available in Biota. Please update these databases before the ENZYME database.")

        # Deleting the database...
        self.log_info_message("Deleting the ENZYME database...")
        DbService.drop_biota_tables([Enzyme])

        # ... to build it from 0
        self.log_info_message("Creating the ENZYME database...")
        DbService.create_biota_tables([Enzyme])

        # Check that all url exist and work
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("all files were found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir, message_dispatcher=self.message_dispatcher)

        # ------------- Create ENZYME ------------- #
        # download BKMS file
        bkms_file = file_downloader.download_file_if_missing(
            params["bkms_file"], filename="Reactions_BKMS.tar.gz", decompress_file=True)

        # download EXPASY file
        expasy_file = file_downloader.download_file_if_missing(
            params["expasy_file"], filename="enzclass.txt")

        # download TAXONOMY file
        taxdump_files = file_downloader.download_file_if_missing(
            params["taxdump_files"], filename="taxdump.tar.gz", decompress_file=True)

        # download BTO file
        bto_file = file_downloader.download_file_if_missing(
            params["bto_file"], filename="bto.owl")

        # download Compound File
        compound_file = file_downloader.download_file_if_missing(
            params["compound_file"], filename="chebi.obo")

        EnzymeService.create_enzyme_db(
            brenda_file=input_file.path, bkms_file=bkms_file, expasy_file=expasy_file, taxonomy_file=taxdump_files,
            bto_file=bto_file, compound_file='/lab/user/chebi.obo')
