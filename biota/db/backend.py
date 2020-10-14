# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import time
from gws.model import Process
from gws.Logger import Logger

from biota.db.go import GO
from biota.db.sbo import SBO
from biota.db.bto import BTO
from biota.db.eco import ECO
from biota.db.taxonomy import Taxonomy
from biota.db.compound import Compound
from biota.db.enzyme import Enzyme
from biota.db.reaction import Reaction
from biota.db.fasta import Fasta

class DbCreator(Process):

    input_specs = {}
    output_specs = {}
    config_specs =  {
        "go_file"                   : {"type": str, "default": "./go/go.obo"},
        "sbo_file"                  : {"type": str, "default": "./sbo/sbo.obo"},
        "eco_file"                  : {"type": str, "default": "./eco/eco.obo"},
        "chebi_file"                : {"type": str, "default": "../chebi/obo/chebi.obo"},
        "bto_file"                  : {"type": str, "default": "./brenda/bto/bto.json"},
        "pwo_file"                  : {"type": str, "default": "./pwo/pwo.obo"},
        "brenda_file"               : {"type": str, "default": "./brenda/brenda/brenda_download.txt"},
        "bkms_file"                 : {"type": str, "default": "./bkms/Reactions_BKMS.csv"},
        "fasta_file"                : {"type": str, "default": "./uniprot/uniprot_sprot.fasta"},
        "ncbi_node_file"            : {"type": str, "default": "./ncbi/taxdump/nodes.dmp"},
        "ncbi_name_file"            : {"type": str, "default": "./ncbi/taxdump/names.dmp"},
        "ncbi_division_file"        : {"type": str, "default": "./ncbi/taxdump/division.dmp"},
        "ncbi_citation_file"        : {"type": str, "default": "./ncbi/taxdump/citations.dmp"},
        "rhea_kegg_reaction_file"   : {"type": str, "default": "./rhea/kegg/rhea-kegg.reaction"},
        "rhea_direction_file"       : {"type": str, "default": "./rhea/tsv/rhea-directions.tsv"},
        "rhea2ecocyc_file"          : {"type": str, "default": "./rhea/tsv/rhea2ecocyc.tsv"},
        "rhea2metacyc_file"         : {"type": str, "default": "./rhea/tsv/rhea2metacyc.tsv"},
        "rhea2macie_file"           : {"type": str, "default": "./rhea/tsv/rhea2macie.tsv"},
        "rhea2kegg_reaction_file"   : {"type": str, "default": "./rhea/tsv/rhea2kegg_reaction.tsv"},
        "rhea2ec_file"              : {"type": str, "default": "./rhea/tsv/rhea2ec.tsv"},
        "rhea2reactome_file"        : {"type": str, "default": "./rhea/tsv/rhea2reactome.tsv"},
        "biota:db_dir"              : {"type": str},
        "biota:biodata_dir"         : {"type": str},
        "biota:testdata_dir"        : {"type": str},
    }

    def task( self ):

        if GO.table_exists():
            Logger.error(Exception("DbCreator", "task", "Biodata databases already exist"))

        # drop tables
        GO.drop_table()
        SBO.drop_table()
        BTO.drop_table()
        ECO.drop_table()
        Taxonomy.drop_table()
        Compound.drop_table()
        Enzyme.drop_table()
        Reaction.drop_table()
        #EnzymeAnnotation.drop_table()

        # create tables
        GO.create_table()
        SBO.create_table()
        BTO.create_table()
        ECO.create_table()
        Taxonomy.create_table()
        Compound.create_table()
        Enzyme.create_table()
        Reaction.create_table()

        Logger.info("Start creating biota_db...")

        params = (self.config.params).copy()    #get a copy
        params['job'] = self.get_active_job()

        # check that all paths exists
        Logger.info("Check that all biodata files exist...")
        biodata_dir = self.get_param("biota:biodata_dir")
        for k in params:
            if k.endswith("_file"):
                file_path = os.path.join(biodata_dir, params[k])
                if not os.path.exists(file_path):
                    Logger.error(Exception("Biodata file {file_path} does not exist"))

        # ------------- Create GO ------------- #
        Logger.info("Step 1 | Saving go and go_ancestors...")
        start_time = time.time()
        
        GO.create_go_db(biodata_dir, **params)
        len_go = GO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))
        
        # ------------- Create SBO ------------- #
        Logger.info("Step 2 | Saving sbo and sbo_ancestors...")
        start_time = time.time()
        SBO.create_sbo_db(biodata_dir, **params)
        len_sbo = SBO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))
        
        # ------------------- Create BTO ----------------- #
        Logger.info("Step 3 | Saving bto and bto_ancestors...")
        start_time = time.time()
        BTO.create_bto_db(biodata_dir, **params)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))
        
        # ------------------- Create ECO ----------------- #
        Logger.info("Step 4 | Saving eco and eco_ancestors...")
        start_time = time.time()
        ECO.create_eco_db(biodata_dir, **params)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))
        
        # ---------------- Create Compound --------------- #
        Logger.info("Step 5 | Saving chebi compounds...")
        start_time = time.time()
        Compound.create_compound_db(biodata_dir, **params)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # ---------------- Create Taxonomy --------------- #
        Logger.info("Step 6 | Saving ncbi taxonomy...")
        start_time = time.time()
        Taxonomy.create_taxonomy_db(biodata_dir, **params)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))

        # ---------------- Create Fasta --------------- #
        Logger.info("Step 7 | Saving chebi fasta...")
        start_time = time.time()
        Fasta.create_fasta_db(biodata_dir, **params)
        len_fasta = Fasta.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #fasta = {} ".format(elapsed_time/60, len_fasta))


        # ------------------ Create Enzyme --------------- #
        Logger.info("Step 8 | Saving brenda enzymes and enzyme_btos...")
        start_time = time.time()
        Enzyme.create_enzyme_db(biodata_dir, **params)
        len_enzyme = Enzyme.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #enzymes = {} ".format(elapsed_time/60, len_enzyme))
        
        # ---------------- Create Reactions -------------- #
        Logger.info("Step 9 | Saving rhea reactions...")
        start_time = time.time()
        Reaction.create_reaction_db(biodata_dir, **params)
        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        Logger.info("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))
