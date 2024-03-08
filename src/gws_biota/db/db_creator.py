# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import time
import requests
import re

from typing import List, Type
from gws_biota import (BTO, ECO, GO, SBO, Compound, Enzyme, Pathway, Protein,
                       Reaction, Taxonomy)
from gws_biota.bto.bto_service import BTOService
from gws_biota.compound.compound_service import CompoundService
from gws_biota.eco.eco_service import ECOService
from gws_biota.enzyme.enzyme_service import EnzymeService
from gws_biota.go.go_service import GOService
from gws_biota.pathway.pathway_service import PathwayService
from gws_biota.protein.protein_service import ProteinService
from gws_biota.reaction.reaction_service import ReactionService
from gws_biota.sbo.sbo_service import SBOService
from gws_biota.taxonomy.taxonomy_service import TaxonomyService
from gws_core import (BadRequestException, ConfigParams, Logger, ModelService,
                      Resource, Settings, StrParam, Task, TaskInputs,
                      TaskOutputs, resource_decorator, task_decorator, InputSpecs, OutputSpecs,
                      FileDownloader, Settings)
from gws_core.extra import BaseModelService

from ..eco.eco import ECO, ECOAncestor
from .db_manager import DbManager
from ..base.base import Base
from ..base.protected_base_model import ProtectedBaseModel


@task_decorator("DbCreator")
class DbCreator(Task):
    input_specs = InputSpecs({})
    output_specs = OutputSpecs({})
    config_specs = {
        # "go_file": StrParam(default_value="https://current.geneontology.org/ontology/go.obo"),
        # "sbo_file": StrParam(default_value="https://raw.githubusercontent.com/EBI-BioModels/SBO/2143b2973f8912db9d4324a4fe543aabcd8f8ba7/SBO_OBO.obo"),
        # "eco_file": StrParam(default_value="https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo"),
        # "chebi_file": StrParam(default_value="https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo"),
        # "bto_file": StrParam(default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl"),
        # "pwo_file": StrParam(default_value="https://download.rgd.mcw.edu/ontology/pathway/pathway.obo"),
        # "reactome_pathways_file": StrParam(default_value="https://reactome.org/download/current/ReactomePathways.txt"),
        # "reactome_pathway_relations_file": StrParam(default_value="https://reactome.org/download/current/ReactomePathwaysRelation.txt"),
        # "reactome_chebi_pathways_file": StrParam(default_value="https://reactome.org/download/current/ChEBI2Reactome.txt"),
        # "taxdump_files": StrParam(default_value="https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"),
        # "protein_file": StrParam(default_value="https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz"),
        "rhea_direction_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea-directions.tsv"),
        "rhea2ecocyc_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2ecocyc.tsv"),
        "rhea2metacyc_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2metacyc.tsv"),
        "rhea2macie_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2macie.tsv"),
        "rhea2kegg_reaction_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2kegg%5Freaction.tsv"),
        "rhea2ec_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2ec.tsv"),
        "rhea2reactome_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2reactome.tsv"),
        # "brenda_file": StrParam(default_value="/"),
        # "bkms_file": StrParam(default_value="https://bkms.brenda-enzymes.org/download/Reactions_BKMS.tar.gz"),
        # "expasy_enzclass_file": StrParam(default_value="https://raw.githubusercontent.com/google-research/proteinfer/540773f988005cc5ed834210d1477e4db1f141e6/testdata/enzclass.txt"),
    }

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        self.init_db()

        # check that all paths exists
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        i = 0
        self.log_info_message("All biodata files found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------------- Create ECO ----------------- #
        # i = i+1
        # self.log_info_message(f"Step {i} | Saving eco and eco_ancestors...")
        # start_time = time.time()

        # # download file
        # eco_file = file_downloader.download_file_if_missing(
        #     params["eco_file"], filename="eco.obo")

        # ECOService.create_eco_db(destination_dir, eco_file)
        # len_eco = ECO.select().count()
        # elapsed_time = time.time() - start_time
        # self.log_info_message("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))

        # # ------------- Create GO ------------- #
        # i = i+1
        # self.log_info_message(f"Step {i} | Saving go and go_ancestors...")
        # start_time = time.time()

        # # download file
        # go_file = file_downloader.download_file_if_missing(
        #     params["go_file"], filename="go.obo")

        # GOService.create_go_db(destination_dir, go_file)
        # len_go = GO.select().count()
        # elapsed_time = time.time() - start_time
        # self.log_info_message("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))

        # ------------- Create SBO ------------- #
        # i = i+1
        # self.log_info_message(f"Step {i} | Saving sbo and sbo_ancestors...")
        # start_time = time.time()

        # # download file
        # sbo_file = file_downloader.download_file_if_missing(
        #     params["sbo_file"], filename="sbo.obo")

        # SBOService.create_sbo_db(destination_dir, sbo_file)
        # len_sbo = SBO.select().count()
        # elapsed_time = time.time() - start_time
        # self.log_info_message("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))

        # ------------------- Create BTO ----------------- #
        # i = i+1
        # self.log_info_message(f"Step {i} | Saving bto and bto_ancestors...")
        # start_time = time.time()

        # # download file
        # bto_file = file_downloader.download_file_if_missing(
        #     params["bto_file"], filename="bto.owl")

        # BTOService.create_bto_db(destination_dir, bto_file)
        # len_bto = BTO.select().count()
        # elapsed_time = time.time() - start_time
        # self.log_info_message("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))

        # ---------------- Create Compound --------------- #
        # i = i+1
        # self.log_info_message(f"Step {i} | Saving chebi compounds...")
        # start_time = time.time()

        # # download file
        # chebi_file = file_downloader.download_file_if_missing(
        #     params["chebi_file"], filename="chebi.obo")

        # CompoundService.create_compound_db(destination_dir, chebi_file)
        # len_compound = Compound.select().count()
        # elapsed_time = time.time() - start_time
        # self.log_info_message("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # ---------------- Create Pathway --------------- #
        i = i+1
        self.log_info_message(f"Step {i} | Saving pathways...")
        start_time = time.time()

        # download pathway file
        pwo_file = file_downloader.download_file_if_missing(
            params["pwo_file"], filename="pathway.obo")

        # download reactome pathway file
        reactome_pathways_file = file_downloader.download_file_if_missing(
            params["reactome_pathways_file"], filename="ReactomePathways.txt")

        # download reactome pathway relation pathway file
        reactome_pathway_relations_file = file_downloader.download_file_if_missing(
            params["reactome_pathway_relations_file"], filename="ReactomePathwaysRelation.txt")

        # download reactome pathway relation pathway file
        reactome_chebi_pathways_file = file_downloader.download_file_if_missing(
            params["reactome_chebi_pathways_file"], filename="ChEBI2Reactome.txt")

        PathwayService.create_pathway_db(destination_dir, pwo_file, reactome_pathways_file,
                                         reactome_pathway_relations_file, reactome_chebi_pathways_file)
        len_pathways = Pathway.select().count()
        elapsed_time = time.time() - start_time
        self.log_info_message("... done in {:10.2f} min for #pathway = {} ".format(elapsed_time/60, len_pathways))

        # ---------------- Create Taxonomy --------------- #
        i = i+1
        self.log_info_message(f"Step {i} | Saving ncbi taxonomy...")
        start_time = time.time()

        # download taxonomy files
        taxdump_files = file_downloader.download_file_if_missing(
            params["taxdump_files"], filename="taxdump.tar.gz", decompress_file=True)

        TaxonomyService.create_taxonomy_db(destination_dir, taxdump_files)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        self.log_info_message("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))

        # ---------------- Create Protein --------------- #
        i = i+1
        self.log_info_message(f"Step {i} | Saving proteins...")
        start_time = time.time()

        # download file
        protein_file = file_downloader.download_file_if_missing(
            params["protein_file"], filename="uniprot_sprot")

        ProteinService.create_protein_db(destination_dir, protein_file)
        len_protein = Protein.select().count()
        elapsed_time = time.time() - start_time
        self.log_info_message("... done in {:10.2f} min for #protein = {} ".format(elapsed_time/60, len_protein))

        # ------------------ Create Enzyme --------------- #
        i = i+1
        self.log_info_message(f"Step {i} | Saving brenda enzymes and enzyme_btos...")
        start_time = time.time()
        EnzymeService.create_enzyme_db(biodata_dir, **cls.params)
        len_enzyme = Enzyme.select().count()
        elapsed_time = time.time() - start_time
        self.log_info_message("... done in {:10.2f} min for #enzymes = {} ".format(elapsed_time/60, len_enzyme))

        # ---------------- Create Reactions -------------- #
        i = i+1
        self.log_info_message(f"Step {i} | Saving rhea reactions...")
        start_time = time.time()

        # creation of rhea_reactions.txt file ----> à mettre dans une fonction ultérieurement pour alléger le code
        url = "https://www.rhea-db.org/rhea/?query=uniprot:*&columns=rhea-id,equation,chebi-id,ec&format=tsv"
        response = requests.get(url)

        with open(f"{destination_dir}/rhea_reactions.txt", 'w', encoding='utf-8') as file:
            # Ignorer la première ligne qui est l'en-tête
            lines = response.text.splitlines()[1:]

            for ligne in lines:
                colonnes = ligne.split('\t')

                operators_in_def = re.findall(r"(\ [\+\=]\ )", colonnes[1])
                definition = re.split("\+|\=", colonnes[1])
                chebi_ids = colonnes[2].split(";")

                file.write(f"ENTRY       {colonnes[0]}\n")

                # Vérification de la présence de la colonne "equation"
                if len(colonnes) > 1 and colonnes[1]:
                    file.write(f"DEFINITION  {colonnes[1]}\n")

                # Vérification de la présence de la colonne "chebi-id"
                if len(colonnes) > 2 and colonnes[2]:
                    file.write("EQUATION    ")
                    # Réécriture de l'équation : CHEBI:58758;CHEBI:16842;CHEBI:57925 -> CHEBI:58758 = CHEBI:16842 + CHEBI:57925
                    for index, value in enumerate(chebi_ids):
                        if index < len(operators_in_def):
                            file.write(f"{value} {operators_in_def[index]} ")
                        else:
                            file.write(f"{value} ")
                    file.write("\n")

                # Vérification de la présence de la colonne "ec"
                if len(colonnes) > 3 and colonnes[3]:
                    enzymes = re.split(":|;", colonnes[3])

                    file.write(f"ENZYME      ")
                    for enzyme in enzymes:
                        if enzyme == "EC":
                            continue

                        file.write(f"{enzyme}       ")
                    file.write("\n")
                file.write("///\n")

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

        ReactionService.create_reaction_db(
            destination_dir, f"{destination_dir}/rhea_reactions.txt", rhea_direction_file, rhea2ecocyc_file,
            rhea2metacyc_file, rhea2macie_file, rhea2kegg_reaction_file, rhea2ec_file, rhea2reactome_file)

        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        self.log_info_message("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))

    def init_db(self):
        """
        Create tables
        """
        self.log_info_message("Initializing biota db")
        DbManager._DEACTIVATE_PROTECTION_ = True

        biota_models = ProtectedBaseModel.inheritors()

        self.log_info_message("Deleting biota tables")
        try:
            self.drop_biota_tables(biota_models)
        except Exception as err:
            self.log_error_message(f'Error during drop, recreating tables. Error: {err}')
            self.create_biota_tables(biota_models)
            raise err

        self.log_info_message("Creating biota tables")
        self.create_biota_tables(biota_models)

        if not ECO.table_exists():
            raise BadRequestException("Cannot create tables")

        if not ECOAncestor.table_exists():
            raise BadRequestException("Cannot create ancestor tables")

        DbManager._DEACTIVATE_PROTECTION_ = False

        self.log_info_message("Biota db initialized")

    def drop_biota_tables(self, biota_models: List[Type[Base]]):
        """
        Drops tables (if they exist)

        :param models: List of model tables to drop
        :type models: `List[type]`
        :param instance: If provided, only the tables of the models that are instances of `model_type` will be droped
        :type model_type: `type`
        """
        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        for biota_model in biota_models:

            if not biota_model.table_exists():
                continue

            # Disable foreigne key on my sql to drop the tables

            # Drop all the tables
            self.log_info_message(f"Dropping table {biota_model.__name__}")
            biota_model.drop_table()
            # DbManager.db.execute_sql(f"DROP TABLE ")

        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")

    def create_biota_tables(self, biota_models: List[Type[Base]]):
        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        for biota_model in biota_models:
            biota_model.create_table()

        for biota_model in biota_models:
            if hasattr(biota_model, 'after_all_tables_init'):
                biota_model.after_all_tables_init()

        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
