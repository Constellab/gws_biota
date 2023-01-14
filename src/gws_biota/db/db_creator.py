# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import time

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
                      TaskOutputs, resource_decorator, task_decorator)

from ..base.base import Base


class DbCreatorHelper:
    params =  {
        "go_file"                   : "./go/go.obo",
        "sbo_file"                  : "./sbo/sbo.obo",
        "eco_file"                  : "./eco/eco.obo",
        "chebi_file"                : "./chebi/obo/chebi.obo",
        "bto_file"                  : "./brenda/bto/bto.json",
        "pwo_file"                  : "./pwo/pwo.obo",
        "brenda_file"               : "./brenda/brenda/brenda_download.txt",
        "bkms_file"                 : "./bkms/Reactions_BKMS.csv",
        "protein_file"              : "./uniprot/uniprot_sprot.fasta",
        "ncbi_node_file"            : "./ncbi/taxdump/nodes.dmp",
        "ncbi_name_file"            : "./ncbi/taxdump/names.dmp",
        "ncbi_division_file"        : "./ncbi/taxdump/division.dmp",
        "ncbi_citation_file"        : "./ncbi/taxdump/citations.dmp",
        "expasy_enzclass_file"      : "./expasy/enzclass.txt",
        "rhea_reaction_file"        : "./rhea/rhea-reactions.txt",
        "rhea_direction_file"       : "./rhea/tsv/rhea-directions.tsv",
        "rhea2ecocyc_file"          : "./rhea/tsv/rhea2ecocyc.tsv",
        "rhea2metacyc_file"         : "./rhea/tsv/rhea2metacyc.tsv",
        "rhea2macie_file"           : "./rhea/tsv/rhea2macie.tsv",
        "rhea2kegg_reaction_file"   : "./rhea/tsv/rhea2kegg_reaction.tsv",
        "rhea2ec_file"              : "./rhea/tsv/rhea2ec.tsv",
        "rhea2reactome_file"        : "./rhea/tsv/rhea2reactome.tsv",
        "reactome_pathways_file"          : "./reactome/ReactomePathways.txt",
        "reactome_pathway_relations_file" : "./reactome/ReactomePathwaysRelation.txt",
        "reactome_chebi_pathways_file"    : "./reactome/ChEBI2Reactome.txt",
    }

    #only allow admin user to run this process
    @classmethod
    def run(cls):
        Logger.info("Start creating biota_db...")
        settings = Settings.get_instance()
        biodata_dir = settings.get_variable("gws_biota:biodata_dir")

        # check that all paths exists
        Logger.info("Check that all biodata files exist...")
        for k in cls.params:
            if k.endswith("_file"):
                file_path = os.path.join(biodata_dir, cls.params[k])
                if not os.path.exists(file_path):
                    raise BadRequestException(f"Biodata file '{file_path}'' does not exist")
        i = 0
        Logger.info("All biodata files found.")

        # ------------------- Create ECO ----------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving eco and eco_ancestors...")
        start_time = time.time()
        ECOService.create_eco_db(biodata_dir, **cls.params)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))

        # ------------- Create GO ------------- #
        i = i+1
        Logger.info(f"Step {i} | Saving go and go_ancestors...")
        start_time = time.time()

        GOService.create_go_db(biodata_dir, **cls.params)
        len_go = GO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))

        # ------------- Create SBO ------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving sbo and sbo_ancestors...")
        start_time = time.time()
        SBOService.create_sbo_db(biodata_dir, **cls.params)
        len_sbo = SBO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))

        # ------------------- Create BTO ----------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving bto and bto_ancestors...")
        start_time = time.time()
        BTOService.create_bto_db(biodata_dir, **cls.params)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))

        # ---------------- Create Compound --------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving chebi compounds...")
        start_time = time.time()
        CompoundService.create_compound_db(biodata_dir, **cls.params)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # ---------------- Create Pathway --------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving pathways...")
        start_time = time.time()
        PathwayService.create_pathway_db(biodata_dir, **cls.params)
        len_pathways = Pathway.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #pathway = {} ".format(elapsed_time/60, len_pathways))

        # ---------------- Create Taxonomy --------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving ncbi taxonomy...")
        start_time = time.time()
        TaxonomyService.create_taxonomy_db(biodata_dir, **cls.params)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))

        # ---------------- Create Protein --------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving proteins...")
        start_time = time.time()
        ProteinService.create_protein_db(biodata_dir, **cls.params)
        len_protein = Protein.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #protein = {} ".format(elapsed_time/60, len_protein))

        # ------------------ Create Enzyme --------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving brenda enzymes and enzyme_btos...")
        start_time = time.time()
        EnzymeService.create_enzyme_db(biodata_dir, **cls.params)
        len_enzyme = Enzyme.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #enzymes = {} ".format(elapsed_time/60, len_enzyme))

        # ---------------- Create Reactions -------------- #
        i=i+1
        Logger.info(f"Step {i} | Saving rhea reactions...")
        start_time = time.time()
        ReactionService.create_reaction_db(biodata_dir, **cls.params)
        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))

@task_decorator("DbCreator")
class DbCreator(Task):
    input_specs = {}
    output_specs = {}
    config_specs =  {
        "go_file"                   : StrParam(default_value="./go/go.obo"),
        "sbo_file"                  : StrParam(default_value="./sbo/sbo.obo"),
        "eco_file"                  : StrParam(default_value="./eco/eco.obo"),
        "chebi_file"                : StrParam(default_value="./chebi/obo/chebi.obo"),
        "bto_file"                  : StrParam(default_value="./brenda/bto/bto.json"),
        "pwo_file"                  : StrParam(default_value="./pwo/pwo.obo"),
        "brenda_file"               : StrParam(default_value="./brenda/brenda/brenda_download.txt"),
        "bkms_file"                 : StrParam(default_value="./bkms/Reactions_BKMS.csv"),
        "protein_file"              : StrParam(default_value="./uniprot/uniprot_sprot.fasta"),
        "ncbi_node_file"            : StrParam(default_value="./ncbi/taxdump/nodes.dmp"),
        "ncbi_name_file"            : StrParam(default_value="./ncbi/taxdump/names.dmp"),
        "ncbi_division_file"        : StrParam(default_value="./ncbi/taxdump/division.dmp"),
        "ncbi_citation_file"        : StrParam(default_value="./ncbi/taxdump/citations.dmp"),
        "expasy_enzclass_file"      : StrParam(default_value="./expasy/enzclass.txt"),
        "rhea_reaction_file"        : StrParam(default_value="./rhea/rhea-reactions.txt"),
        "rhea_direction_file"       : StrParam(default_value="./rhea/tsv/rhea-directions.tsv"),
        "rhea2ecocyc_file"          : StrParam(default_value="./rhea/tsv/rhea2ecocyc.tsv"),
        "rhea2metacyc_file"         : StrParam(default_value="./rhea/tsv/rhea2metacyc.tsv"),
        "rhea2macie_file"           : StrParam(default_value="./rhea/tsv/rhea2macie.tsv"),
        "rhea2kegg_reaction_file"   : StrParam(default_value="./rhea/tsv/rhea2kegg_reaction.tsv"),
        "rhea2ec_file"              : StrParam(default_value="./rhea/tsv/rhea2ec.tsv"),
        "rhea2reactome_file"        : StrParam(default_value="./rhea/tsv/rhea2reactome.tsv"),
        "reactome_pathways_file"          : StrParam(default_value="./reactome/ReactomePathways.txt"),
        "reactome_pathway_relations_file" : StrParam(default_value="./reactome/ReactomePathwaysRelation.txt"),
        "reactome_chebi_pathways_file"    : StrParam(default_value="./reactome/ChEBI2Reactome.txt"),
    }

    #only allow admin user to run this process
    async def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        DbCreatorHelper.run(params)