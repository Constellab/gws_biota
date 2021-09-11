# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import time
from gws_core import (Task, Settings, BadRequestException, 
                        ModelService, Resource, resource_decorator, 
                        task_decorator, ConfigParams, TaskInputs, TaskOutputs, StrParam)

from gws_biota import (GO, SBO, BTO, ECO, Taxonomy, Compound, Enzyme, Reaction, Protein, Pathway)

from gws_biota.go.go_service import GOService
from gws_biota.sbo.sbo_service import SBOService
from gws_biota.bto.bto_service import BTOService
from gws_biota.eco.eco_service import ECOService
from gws_biota.taxonomy.taxonomy_service import TaxonomyService
from gws_biota.compound.compound_service import CompoundService
from gws_biota.enzyme.enzyme_service import EnzymeService
from gws_biota.reaction.reaction_service import ReactionService
from gws_biota.protein.protein_service import ProteinService
from gws_biota.pathway.pathway_service import PathwayService

from ..base.base import Base

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
    async def run(self, config: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        self.add_progress_message("Start creating biota_db...")
        settings = Settings.retrieve()
        biodata_dir = settings.get_variable("gws_biota:biodata_dir")

        # check that all paths exists
        self.add_progress_message("Check that all biodata files exist...")
        for k in config:
            if k.endswith("_file"):
                file_path = os.path.join(biodata_dir, config[k])
                if not os.path.exists(file_path):
                    raise BadRequestException(f"Biodata file '{file_path}'' does not exist")
        i = 0
        
        # ------------------- Create ECO ----------------- #
        i=i+1
        self.update_progress_value(2, f"Step {i} | Saving eco and eco_ancestors...")
        start_time = time.time()
        ECOService.create_eco_db(biodata_dir, **config)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(3, "... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))

        # ------------- Create GO ------------- #
        i = i+1
        self.update_progress_value(4, f"Step {i} | Saving go and go_ancestors...")
        start_time = time.time()
        
        GOService.create_go_db(biodata_dir, **config)
        len_go = GO.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(6, "... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))

        # ------------- Create SBO ------------- #
        i=i+1
        self.update_progress_value(7, f"Step {i} | Saving sbo and sbo_ancestors...")
        start_time = time.time()
        SBOService.create_sbo_db(biodata_dir, **config)
        len_sbo = SBO.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(9, "... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))

        # ------------------- Create BTO ----------------- #
        i=i+1
        self.update_progress_value(10, f"Step {i} | Saving bto and bto_ancestors...")
        start_time = time.time()
        BTOService.create_bto_db(biodata_dir, **config)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(12, "... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))

        # ---------------- Create Compound --------------- #
        i=i+1
        self.update_progress_value(13, f"Step {i} | Saving chebi compounds...")
        start_time = time.time()
        CompoundService.create_compound_db(biodata_dir, **config)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(20, "... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # ---------------- Create Pathway --------------- #
        i=i+1
        self.update_progress_value(21, f"Step {i} | Saving pathways...")
        start_time = time.time()
        PathwayService.create_pathway_db(biodata_dir, **config)
        len_pathways = Pathway.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(25, "... done in {:10.2f} min for #pathway = {} ".format(elapsed_time/60, len_pathways))

        # ---------------- Create Taxonomy --------------- #
        i=i+1
        self.update_progress_value(26, f"Step {i} | Saving ncbi taxonomy...")
        start_time = time.time()
        TaxonomyService.create_taxonomy_db(biodata_dir, **config)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(60, "... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))

        # ---------------- Create Protein --------------- #
        i=i+1
        self.update_progress_value(61, f"Step {i} | Saving proteins...")
        start_time = time.time()
        ProteinService.create_protein_db(biodata_dir, **config)
        len_protein = Protein.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(75, "... done in {:10.2f} min for #protein = {} ".format(elapsed_time/60, len_protein))

        # ------------------ Create Enzyme --------------- #
        i=i+1
        self.update_progress_value(76, f"Step {i} | Saving brenda enzymes and enzyme_btos...")
        start_time = time.time()
        EnzymeService.create_enzyme_db(biodata_dir, **config)
        len_enzyme = Enzyme.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(85, "... done in {:10.2f} min for #enzymes = {} ".format(elapsed_time/60, len_enzyme))

        # ---------------- Create Reactions -------------- #
        i=i+1
        self.update_progress_value(86, f"Step {i} | Saving rhea reactions...")
        start_time = time.time()
        ReactionService.create_reaction_db(biodata_dir, **config)
        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        self.update_progress_value(95, "... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))