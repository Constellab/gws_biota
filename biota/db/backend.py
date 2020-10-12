# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import time
from gws.model import Process
from gws.logger import Logger

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
        "go_file"                   : {"type": str, "default": "./go.obo"},
        "sbo_file"                  : {"type": str, "default": "./sbo.obo"},
        "eco_file"                  : {"type": str, "default": "./eco.obo"},
        "chebi_file"                : {"type": str, "default": "./obo/chebi.obo"},
        "bto_file"                  : {"type": str, "default": "./bto.json"},
        "pwo_file"                  : {"type": str, "default": "./pwo/pwo.obo"},
        "brenda_file"               : {"type": str, "default": "./brenda/brenda_download.txt"},
        "bkms_file"                 : {"type": str, "default": "./bkms/Reactions_BKMS.csv"},
        "fasta_file"                : {"type": str, "default": "./uniprot_sprot.fasta"},
        #"chebi_compound_file"       : {"type": str, "default": "./tsv/compounds.tsv"},
        #"chebi_chemical_data_file"  : {"type": str, "default": "./tsv/chemical_data.tsv"},
        #"chebi_sdf_file"            : {"type": str, "default": "./sdf/ChEBI_complete.sdf"},
        "ncbi_node_file"            : {"type": str, "default": "./taxdump/nodes.dmp"},
        "ncbi_name_file"            : {"type": str, "default": "./taxdump/names.dmp"},
        "ncbi_division_file"        : {"type": str, "default": "./taxdump/division.dmp"},
        "ncbi_citation_file"        : {"type": str, "default": "./taxdump/citations.dmp"},
        "rhea_kegg_reaction_file"   : {"type": str, "default": "./kegg/rhea-kegg.reaction"},
        "rhea_direction_file"       : {"type": str, "default": "./tsv/rhea-directions.tsv"},
        "rhea2ecocyc_file"          : {"type": str, "default": "./tsv/rhea2ecocyc.tsv"},
        "rhea2metacyc_file"         : {"type": str, "default": "./tsv/rhea2metacyc.tsv"},
        "rhea2macie_file"           : {"type": str, "default": "./tsv/rhea2macie.tsv"},
        "rhea2kegg_reaction_file"   : {"type": str, "default": "./tsv/rhea2kegg_reaction.tsv"},
        "rhea2ec_file"              : {"type": str, "default": "./tsv/rhea2ec.tsv"},
        "rhea2reactome_file"        : {"type": str, "default": "./tsv/rhea2reactome.tsv"},
        "biota:db_dir"              : {"type": str},
        "biota:biodata_dir"         : {"type": str},
        "biota:testdata_dir"        : {"type": str},
        "biota:fasta_biodata_dir"   : {"type": str},
        "biota:brenda_biodata_dir"  : {"type": str},
        "biota:bkms_biodata_dir"    : {"type": str},
        "biota:chebi_biodata_dir"   : {"type": str},
        "biota:go_biodata_dir"      : {"type": str},
        "biota:eco_biodata_dir"     : {"type": str},
        "biota:sbo_biodata_dir"     : {"type": str},
        "biota:bto_biodata_dir"     : {"type": str},
        "biota:pwo_biodata_dir"     : {"type": str},
        "biota:rhea_biodata_dir"    : {"type": str},
        "biota:taxonomy_biodata_dir": {"type": str}
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

        logger = Logger()
        logger.info("Start creating biota_db...")

        params = (self.config.params).copy()    #get a copy
        params['job'] = self.get_active_job()

        # ---------------- Create Fasta --------------- #
        logger.info("Step 7 | Saving chebi fasta...")
        start_time = time.time()
        fasta_biodata_dir = self.get_param("biota:fasta_biodata_dir")
        Fasta.create_fasta_db(fasta_biodata_dir, **params)
        len_fasta = Fasta.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #fasta = {} ".format(elapsed_time/60, len_fasta))


        # ------------- Create GO ------------- #
        logger.info("Step 1 | Saving go and go_ancestors...")
        start_time = time.time()
        go_biodata_dir = self.get_param("biota:go_biodata_dir")
        GO.create_go_db(go_biodata_dir, **params)
        len_go = GO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))
        
        # ------------- Create SBO ------------- #
        logger.info("Step 2 | Saving sbo and sbo_ancestors...")
        start_time = time.time()
        sbo_biodata_dir = self.get_param("biota:sbo_biodata_dir")
        SBO.create_sbo_db(sbo_biodata_dir, **params)
        len_sbo = SBO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))
        
        # ------------------- Create BTO ----------------- #
        logger.info("Step 3 | Saving bto and bto_ancestors...")
        start_time = time.time()
        bto_biodata_dir = self.get_param("biota:bto_biodata_dir")
        BTO.create_bto_db(bto_biodata_dir, **params)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))
        
        # ------------------- Create ECO ----------------- #
        logger.info("Step 4 | Saving eco and eco_ancestors...")
        start_time = time.time()
        eco_biodata_dir = self.get_param("biota:eco_biodata_dir")
        ECO.create_eco_db(eco_biodata_dir, **params)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))
        
        # ---------------- Create Compound --------------- #
        logger.info("Step 5 | Saving chebi compounds...")
        start_time = time.time()
        chebi_biodata_dir = self.get_param("biota:chebi_biodata_dir")
        Compound.create_compound_db(chebi_biodata_dir, **params)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # ---------------- Create Taxonomy --------------- #
        logger.info("Step 6 | Saving ncbi taxonomy...")
        start_time = time.time()
        ncbi_biodata_dir = self.get_param("biota:taxonomy_biodata_dir")
        Taxonomy.create_taxonomy_db(ncbi_biodata_dir, **params)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))

        # ---------------- Create Fasta --------------- #
        logger.info("Step 7 | Saving chebi fasta...")
        start_time = time.time()
        fasta_biodata_dir = self.get_param("biota:fasta_biodata_dir")
        Fasta.create_fasta_db(fasta_biodata_dir, **params)
        len_fasta = Fasta.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #fasta = {} ".format(elapsed_time/60, len_fasta))


        # ------------------ Create Enzyme --------------- #
        logger.info("Step 8 | Saving brenda proteins and protein_btos...")
        start_time = time.time()
        brenda_biodata_dir = self.get_param("biota:brenda_biodata_dir")
        Enzyme.create_protein_db(brenda_biodata_dir, **params)
        len_protein = Enzyme.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #proteins = {} ".format(elapsed_time/60, len_protein))
        
        # ---------------- Create Reactions -------------- #
        logger.info("Step 9 | Saving rhea reactions...")
        start_time = time.time()
        rhea_biodata_dir = self.get_param("biota:rhea_biodata_dir")
        Reaction.create_reaction_db(rhea_biodata_dir, **params)
        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))
