# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import time
from gws.process import Process
from gws.settings import Settings
from gws.exception.bad_request_exception import BadRequestException

from biota.base import Base
from biota.go import GO
from biota.sbo import SBO
from biota.bto import BTO
from biota.eco import ECO
from biota.taxonomy import Taxonomy
from biota.compound import Compound
from biota.enzyme import Enzyme
from biota.reaction import Reaction
from biota.protein import Protein
from biota.pathway import Pathway

class DbCreator(Process):
    input_specs = {}
    output_specs = {}
    config_specs =  { 
        "go_file"                   : {"type": str, "default": "./go/go.obo"},
        "sbo_file"                  : {"type": str, "default": "./sbo/sbo.obo"},
        "eco_file"                  : {"type": str, "default": "./eco/eco.obo"},
        "chebi_file"                : {"type": str, "default": "./chebi/obo/chebi.obo"},
        "bto_file"                  : {"type": str, "default": "./brenda/bto/bto.json"},
        "pwo_file"                  : {"type": str, "default": "./pwo/pwo.obo"},
        "brenda_file"               : {"type": str, "default": "./brenda/brenda/brenda_download.txt"},
        "bkms_file"                 : {"type": str, "default": "./bkms/Reactions_BKMS.csv"},
        "protein_file"              : {"type": str, "default": "./uniprot/uniprot_sprot.fasta"},
        "ncbi_node_file"            : {"type": str, "default": "./ncbi/taxdump/nodes.dmp"},
        "ncbi_name_file"            : {"type": str, "default": "./ncbi/taxdump/names.dmp"},
        "ncbi_division_file"        : {"type": str, "default": "./ncbi/taxdump/division.dmp"},
        "ncbi_citation_file"        : {"type": str, "default": "./ncbi/taxdump/citations.dmp"},
        "expasy_enzclass_file"      : {"type": str, "default": "./expasy/enzclass.txt"},
        "rhea_reaction_file"        : {"type": str, "default": "./rhea/rhea-reactions.txt"},
        "rhea_direction_file"       : {"type": str, "default": "./rhea/tsv/rhea-directions.tsv"},
        "rhea2ecocyc_file"          : {"type": str, "default": "./rhea/tsv/rhea2ecocyc.tsv"},
        "rhea2metacyc_file"         : {"type": str, "default": "./rhea/tsv/rhea2metacyc.tsv"},
        "rhea2macie_file"           : {"type": str, "default": "./rhea/tsv/rhea2macie.tsv"},
        "rhea2kegg_reaction_file"   : {"type": str, "default": "./rhea/tsv/rhea2kegg_reaction.tsv"},
        "rhea2ec_file"              : {"type": str, "default": "./rhea/tsv/rhea2ec.tsv"},
        "rhea2reactome_file"        : {"type": str, "default": "./rhea/tsv/rhea2reactome.tsv"},
        "reactome_pathways_file"          : {"type": str, "default": "./reactome/ReactomePathways.txt"},
        "reactome_pathway_relations_file" : {"type": str, "default": "./reactome/ReactomePathwaysRelation.txt"},
        "reactome_chebi_pathways_file"    : {"type": str, "default": "./reactome/ChEBI2Reactome.txt"},        
    }

    #only allow admin user to run this process
    _allowed_user = Process.USER_ADMIN

    async def task( self ):
        # deactivate full_text_search functionalitie is required
        if ECO.table_exists():
            if ECO.select().count():
                raise BadRequestException("An none empty biota database already exists")
        else:
            from gws.service.model_service import ModelService
            ModelService.create_tables(model_type=Base)

        self.progress_bar.add_message("Start creating biota_db...", show_info=True)
        params = self.config.params.copy()    #get a copy
        settings = Settings.retrieve()
        dirs = settings.get_data("dirs")
        biodata_dir = dirs["biota:biodata_dir"]

        # check that all paths exists
        self.progress_bar.add_message("Check that all biodata files exist...", show_info=True)
        for k in params:
            if k.endswith("_file"):
                file_path = os.path.join(biodata_dir, params[k])
                if not os.path.exists(file_path):
                    raise BadRequestException(f"Biodata file '{file_path}'' does not exist")
        i = 0
        
        # ------------------- Create ECO ----------------- #
        i=i+1
        self.progress_bar.set_value(2, f"Step {i} | Saving eco and eco_ancestors...", show_info=True)
        start_time = time.time()
        ECO.create_eco_db(biodata_dir, **params)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(3, "... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco), show_info=True)

        # ------------- Create GO ------------- #
        i = i+1
        self.progress_bar.set_value(4, f"Step {i} | Saving go and go_ancestors...", show_info=True)
        start_time = time.time()
        
        GO.create_go_db(biodata_dir, **params)
        len_go = GO.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(6, "... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go), show_info=True)

        # ------------- Create SBO ------------- #
        i=i+1
        self.progress_bar.set_value(7, f"Step {i} | Saving sbo and sbo_ancestors...", show_info=True)
        start_time = time.time()
        SBO.create_sbo_db(biodata_dir, **params)
        len_sbo = SBO.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(9, "... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo), show_info=True)

        # ------------------- Create BTO ----------------- #
        i=i+1
        self.progress_bar.set_value(10, f"Step {i} | Saving bto and bto_ancestors...", show_info=True)
        start_time = time.time()
        BTO.create_bto_db(biodata_dir, **params)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(12, "... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto), show_info=True)

        # ---------------- Create Compound --------------- #
        i=i+1
        self.progress_bar.set_value(13, f"Step {i} | Saving chebi compounds...", show_info=True)
        start_time = time.time()
        Compound.create_compound_db(biodata_dir, **params)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(20, "... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound), show_info=True)

        # ---------------- Create Pathway --------------- #
        i=i+1
        self.progress_bar.set_value(21, f"Step {i} | Saving pathways...", show_info=True)
        start_time = time.time()
        Pathway.create_pathway_db(biodata_dir, **params)
        len_pathways = Pathway.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(25, "... done in {:10.2f} min for #pathway = {} ".format(elapsed_time/60, len_pathways), show_info=True)

        # ---------------- Create Taxonomy --------------- #
        i=i+1
        self.progress_bar.set_value(26, f"Step {i} | Saving ncbi taxonomy...", show_info=True)
        start_time = time.time()
        Taxonomy.create_taxonomy_db(biodata_dir, **params)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(60, "... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy), show_info=True)

        # ---------------- Create Protein --------------- #
        i=i+1
        self.progress_bar.set_value(61, f"Step {i} | Saving proteins...", show_info=True)
        start_time = time.time()
        Protein.create_protein_db(biodata_dir, **params)
        len_protein = Protein.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(75, "... done in {:10.2f} min for #protein = {} ".format(elapsed_time/60, len_protein), show_info=True)

        # ------------------ Create Enzyme --------------- #
        i=i+1
        self.progress_bar.set_value(76, f"Step {i} | Saving brenda enzymes and enzyme_btos...", show_info=True)
        start_time = time.time()
        Enzyme.create_enzyme_db(biodata_dir, **params)
        len_enzyme = Enzyme.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(85, "... done in {:10.2f} min for #enzymes = {} ".format(elapsed_time/60, len_enzyme), show_info=True)

        # ---------------- Create Reactions -------------- #
        i=i+1
        self.progress_bar.set_value(86, f"Step {i} | Saving rhea reactions...", show_info=True)
        start_time = time.time()
        Reaction.create_reaction_db(biodata_dir, **params)
        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        self.progress_bar.set_value(95, "... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea), show_info=True)