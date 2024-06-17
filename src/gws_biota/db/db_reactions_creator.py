

import re
import requests

from gws_core import (ConfigParams, Settings, StrParam, Task, TaskInputs, Text,
                      TaskOutputs, task_decorator, InputSpecs, InputSpec, OutputSpec, OutputSpecs,
                      FileDownloader)

from gws_biota import Reaction
from gws_biota.reaction.reaction_service import ReactionService
from ..compound.compound_service import Compound
from ..taxonomy.taxonomy import Taxonomy
from ..enzyme.enzyme_service import Enzyme

from .db_service import DbService


@task_decorator("ReactionDBCreator")
class ReactionDBCreator(Task):
    input_specs = InputSpecs({"input_compound": InputSpec(Text, human_name="link to compound", is_optional=True),
                              "input_taxonomy": InputSpec(Text, human_name="link to taxonomy", is_optional=True),
                              "input_enzyme": InputSpec(Text, human_name="link to enzyme", is_optional=True)})

    output_specs = OutputSpecs({"output_text": OutputSpec(Text, is_optional=True)})
    config_specs = {"rhea_direction_file": StrParam(
        default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea-directions.tsv"),
        "rhea2ecocyc_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2ecocyc.tsv"),
        "rhea2metacyc_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2metacyc.tsv"),
        "rhea2macie_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2macie.tsv"),
        "rhea2kegg_reaction_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2kegg%5Freaction.tsv"),
        "rhea2ec_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2ec.tsv"),
        "rhea2reactome_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2reactome.tsv"),
        "rhea_reactions_file": StrParam(default_value="https://www.rhea-db.org/rhea/?query=uniprot:*&columns=rhea-id,equation,chebi-id,ec&format=tsv")}

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        len_bto = Compound.select().count()
        len_taxonomy = Taxonomy.select().count()
        len_pathway = Enzyme.select().count()

        # Check that dependent databases are available before downloading enzyme data.
        if len_bto == 0 or len_taxonomy == 0 or len_pathway == 0:
            raise Exception(
                "No data from the TAXONOMY, COMPOUND or ENZYME databases available in Biota. Please update these databases before the ENZYME database.")

        # Deleting the database...
        self.log_info_message("Deleting the RHEA database...")
        DbService.drop_biota_tables([Reaction])

        # ... to build it from 0
        self.log_info_message("Creating the RHEA database...")
        DbService.create_biota_tables([Reaction])

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

        # ------------- Create RHEA ------------- #
        # download direction file
        rhea_direction_file = file_downloader.download_file_if_missing(
            params["rhea_direction_file"], filename="rhea-directions.tsv")

        # download ecocyc file
        rhea2ecocyc_file = file_downloader.download_file_if_missing(
            params["rhea2ecocyc_file"], filename="rhea2ecocyc.tsv")

        # download metacyc file
        rhea2metacyc_file = file_downloader.download_file_if_missing(
            params["rhea2metacyc_file"], filename="rhea2metacyc.tsv")

        # download macie file
        rhea2macie_file = file_downloader.download_file_if_missing(
            params["rhea2macie_file"], filename="rhea2macie.tsv")

        # download kegg file
        rhea2kegg_reaction_file = file_downloader.download_file_if_missing(
            params["rhea2kegg_reaction_file"], filename="rhea2kegg.tsv")

        # download ec file
        rhea2ec_file = file_downloader.download_file_if_missing(
            params["rhea2ec_file"], filename="rhea2ec.tsv")

        # download reactome file
        rhea2reactome_file = file_downloader.download_file_if_missing(
            params["rhea2reactome_file"], filename="rhea2reactome.tsv")

        # download and construct reactions file
        rhea_reactions_file = file_downloader.download_file_if_missing(
            params["rhea_reactions_file"], filename="rhea_reactions.tsv")

        with open(rhea_reactions_file, "r", encoding='utf-8') as reactions_file:
            with open(f"{destination_dir}/rhea_reactions.txt", 'w', encoding='utf-8') as new_reactions_file:
                # Ignore the first line which is the headere
                lines = reactions_file.readlines()

                for ligne in lines[1:]:
                    colonnes = ligne.split('\t')

                    operators_in_def = re.findall(r"(\ [\+\=]\ )", colonnes[1])
                    chebi_ids = colonnes[2].split(";")

                    new_reactions_file.write(f"ENTRY       {colonnes[0]}\n")

                    # Checking the presence of the "equation" column
                    if len(colonnes) > 1 and colonnes[1]:
                        new_reactions_file.write(f"DEFINITION  {colonnes[1]}\n")

                    # Checking the presence of the “chebi-id” column
                    if len(colonnes) > 2 and colonnes[2]:
                        new_reactions_file.write("EQUATION    ")
                        # Rewriting the equation : CHEBI:58758;CHEBI:16842;CHEBI:57925 -> CHEBI:58758 = CHEBI:16842 + CHEBI:57925
                        for index, value in enumerate(chebi_ids):
                            if index < len(operators_in_def):
                                new_reactions_file.write(f"{value} {operators_in_def[index]} ")
                            else:
                                new_reactions_file.write(f"{value} ")
                        new_reactions_file.write("\n")

                    # Checking the presence of the “ec” column
                    if len(colonnes) > 3 and colonnes[3]:
                        enzymes = re.split(":|;", colonnes[3])

                        new_reactions_file.write(f"ENZYME      ")
                        for enzyme in enzymes:
                            if enzyme == "EC":
                                continue

                            new_reactions_file.write(f"{enzyme}")
                    new_reactions_file.write("///\n")

        ReactionService.create_reaction_db(
            destination_dir, f"{destination_dir}/rhea_reactions.txt", rhea_direction_file, rhea2ecocyc_file,
            rhea2metacyc_file, rhea2macie_file, rhea2kegg_reaction_file, rhea2ec_file, rhea2reactome_file)
