# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import time
import requests

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

from ..base.base import Base


class DbCreatorHelper:
    params = {
        #     "bto_file": "https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl",
        #     "pwo_file": "https://download.rgd.mcw.edu/ontology/pathway/pathway.obo",
        #     "brenda_file": "/",
        #     "bkms_file": "https://bkms.brenda-enzymes.org/download/Reactions_BKMS.tar.gz",
        #     "protein_file": "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz",
        #     "ncbi_taxonomy": "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz",
        #     "ncbi_node_file": "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz",
        #     "ncbi_name_file": "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz",
        #     "ncbi_division_file": "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz",
        #     "expasy_enzclass_file": "/",
        #     "rhea_reaction_file": "",
        #     "rhea_direction_file": "",
        #     "rhea2ecocyc_file": "",
        #     "rhea2metacyc_file": "",
        #     "rhea2macie_file": "",
        #     "rhea2kegg_reaction_file": "",
        #     "rhea2ec_file": "",
        #     "rhea2reactome_file": "",
        #     "reactome_pathways_file": "",
        #     "reactome_pathway_relations_file": "",
        #     "reactome_chebi_pathways_file": "",
    }

    # only allow admin user to run this process
    def run(self, params):
        Logger.info("Start creating biota_db...")

        # check that all paths exists
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        i = 0
        Logger.info("All biodata files found.")

        # ------------------- Create ECO ----------------- #
        i = i+1
        Logger.info(f"Step {i} | Saving eco and eco_ancestors...")
        start_time = time.time()

        # download file
        destination_dir = Settings.get_instance().make_temp_dir()
        file_downloader = FileDownloader(destination_dir)
        eco_file = file_downloader.download_file_if_missing(
            params["eco_file"], filename="eco.obo")

        ECOService.create_eco_db(destination_dir, eco_file)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))

        # # ------------- Create GO ------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving go and go_ancestors...")
        # start_time = time.time()

        # # download file
        # destination_dir = Settings.get_instance().make_temp_dir()
        # file_downloader = FileDownloader(destination_dir)
        # go_file = file_downloader.download_file_if_missing(
        #     params["go_file"], filename="go.obo")

        # GOService.create_go_db(destination_dir, go_file)
        # len_go = GO.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))

        # # ------------- Create SBO ------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving sbo and sbo_ancestors...")
        # start_time = time.time()

        # # download file
        # destination_dir = Settings.get_instance().make_temp_dir()
        # file_downloader = FileDownloader(destination_dir)
        # sbo_file = file_downloader.download_file_if_missing(
        #     params["sbo_file"], filename="sbo.obo")

        # SBOService.create_sbo_db(destination_dir, sbo_file)
        # len_sbo = SBO.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))

        # ------------------- Create BTO ----------------- #
        i = i+1
        Logger.info(f"Step {i} | Saving bto and bto_ancestors...")
        start_time = time.time()

        # download file
        destination_dir = Settings.get_instance().make_temp_dir()
        file_downloader = FileDownloader(destination_dir)
        bto_file = file_downloader.download_file_if_missing(
            params["bto_file"], filename="bto.owl")

        BTOService.create_bto_db(destination_dir, bto_file)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))

        # ---------------- Create Compound --------------- #
        i = i+1
        Logger.info(f"Step {i} | Saving chebi compounds...")
        start_time = time.time()

        # download file
        destination_dir = Settings.get_instance().make_temp_dir()
        file_downloader = FileDownloader(destination_dir)
        chebi_file = file_downloader.download_file_if_missing(
            params["chebi_file"], filename="chebi.obo")

        CompoundService.create_compound_db(destination_dir, chebi_file)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # # ---------------- Create Pathway --------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving pathways...")
        # start_time = time.time()
        # PathwayService.create_pathway_db(biodata_dir, **cls.params)
        # len_pathways = Pathway.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} min for #pathway = {} ".format(elapsed_time/60, len_pathways))

        # # ---------------- Create Taxonomy --------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving ncbi taxonomy...")
        # start_time = time.time()
        # TaxonomyService.create_taxonomy_db(biodata_dir, cls.params["ncbi_taxonomy"])
        # len_taxonomy = Taxonomy.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))

        # # ---------------- Create Protein --------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving proteins...")
        # start_time = time.time()
        # ProteinService.create_protein_db(biodata_dir, **cls.params)
        # len_protein = Protein.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} min for #protein = {} ".format(elapsed_time/60, len_protein))

        # # ------------------ Create Enzyme --------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving brenda enzymes and enzyme_btos...")
        # start_time = time.time()
        # EnzymeService.create_enzyme_db(biodata_dir, **cls.params)
        # len_enzyme = Enzyme.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} min for #enzymes = {} ".format(elapsed_time/60, len_enzyme))

        # # ---------------- Create Reactions -------------- #
        # i = i+1
        # Logger.info(f"Step {i} | Saving rhea reactions...")
        # start_time = time.time()
        # ReactionService.create_reaction_db(biodata_dir, **cls.params)
        # len_rhea = Reaction.select().count()
        # elapsed_time = time.time() - start_time
        # Logger.info("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))


@ task_decorator("DbCreator")
class DbCreator(Task):
    input_specs = InputSpecs({})
    output_specs = OutputSpecs({})
    config_specs = {
        "go_file": StrParam(default_value="https://current.geneontology.org/ontology/go.obo"),
        "sbo_file": StrParam(default_value="https://raw.githubusercontent.com/EBI-BioModels/SBO/2143b2973f8912db9d4324a4fe543aabcd8f8ba7/SBO_OBO.obo"),
        "eco_file": StrParam(default_value="https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo"),
        "chebi_file": StrParam(default_value="https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo"),
        "bto_file": StrParam(default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl"),
        # "pwo_file": StrParam(default_value="./pwo/pwo.obo"),
        # "brenda_file": StrParam(default_value="./brenda/brenda/brenda_download.txt"),
        # "bkms_file": StrParam(default_value="./bkms/Reactions_BKMS.csv"),
        # "protein_file": StrParam(default_value="./uniprot/uniprot_sprot.fasta"),
        # "ncbi_node_file": StrParam(default_value="./ncbi/taxdump/nodes.dmp"),
        # "ncbi_name_file": StrParam(default_value="./ncbi/taxdump/names.dmp"),
        # "ncbi_division_file": StrParam(default_value="./ncbi/taxdump/division.dmp"),
        # "ncbi_citation_file": StrParam(default_value="./ncbi/taxdump/citations.dmp"),
        # "expasy_enzclass_file": StrParam(default_value="./expasy/enzclass.txt"),
        # "rhea_reaction_file": StrParam(default_value="./rhea/rhea-reactions.txt"),
        # "rhea_direction_file": StrParam(default_value="./rhea/tsv/rhea-directions.tsv"),
        # "rhea2ecocyc_file": StrParam(default_value="./rhea/tsv/rhea2ecocyc.tsv"),
        # "rhea2metacyc_file": StrParam(default_value="./rhea/tsv/rhea2metacyc.tsv"),
        # "rhea2macie_file": StrParam(default_value="./rhea/tsv/rhea2macie.tsv"),
        # "rhea2kegg_reaction_file": StrParam(default_value="./rhea/tsv/rhea2kegg_reaction.tsv"),
        # "rhea2ec_file": StrParam(default_value="./rhea/tsv/rhea2ec.tsv"),
        # "rhea2reactome_file": StrParam(default_value="./rhea/tsv/rhea2reactome.tsv"),
        # "reactome_pathways_file": StrParam(default_value="./reactome/ReactomePathways.txt"),
        # "reactome_pathway_relations_file": StrParam(default_value="./reactome/ReactomePathwaysRelation.txt"),
        # "reactome_chebi_pathways_file": StrParam(default_value="./reactome/ChEBI2Reactome.txt"),
    }

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        DbCreatorHelper.run(params)
