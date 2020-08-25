# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import time
from gws.prism.model import Process
from gws.logger import Logger

from biota.db.go import GO
from biota.db.sbo import SBO
from biota.db.bto import BTO
from biota.db.eco import ECO
from biota.db.chebi_ontology import ChebiOntology
from biota.db.taxonomy import Taxonomy
from biota.db.compound import Compound
from biota.db.enzyme_function import EnzymeFunction
from biota.db.reaction import Reaction

class DbCreator(Process):

    input_specs = {}
    output_specs = {}
    config_specs =  {
        "go_file"                   : {"type": str, "default": "go.obo"},
        "sbo_file"                  : {"type": str, "default": "sbo.obo"},
        "eco_file"                  : {"type": str, "default": "eco.obo"},
        "chebi_file"                : {"type": str, "default": "./obo/chebi.obo"},
        "bto_file"                  : {"type": str, "default": "bto.json"},
        "pwo_file"                  : {"type": str, "default": "./pwo/pwo.obo"},
        "brenda_file"               : {"type": str, "default": "./brenda/brenda_download.txt"},
        "bkms_file"                 : {"type": str, "default": "./bkms/Reactions_BKMS.csv"},
        "chebi_compound_file"       : {"type": str, "default": "./tsv/compounds.tsv"},
        "chebi_chemical_data_file"  : {"type": str, "default": "./tsv/chemical_data.tsv"},
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
        "biota:biodata_dir"         : {"type": str},
        "biota:testdata_dir"        : {"type": str},
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
            raise Exception("DbCreator", "task", "A databse already exists")

        # drop tables
        GO.drop_table()
        SBO.drop_table()
        BTO.drop_table()
        ECO.drop_table()
        ChebiOntology.drop_table()
        Taxonomy.drop_table()
        Compound.drop_table()
        EnzymeFunction.drop_table()
        Reaction.drop_table()
        #EnzymeAnnotation.drop_table()

        # create tables
        GO.create_table()
        SBO.create_table()
        BTO.create_table()
        ECO.create_table()
        ChebiOntology.create_table()
        Taxonomy.create_table()
        Compound.create_table()
        EnzymeFunction.create_table()
        Reaction.create_table()

        logger = Logger()
        logger.info("Start creating biota_db...")

        params = self.config.params
        params['job'] = self.get_active_job()

        # ------------- Create GO ------------- #
        logger.info("Step 1 | Loading go and go_ancestors...")
        start_time = time.time()
        go_biodata_dir = self.get_param("biota:go_biodata_dir")
        GO.create_go_db(go_biodata_dir, **params)
        len_go = GO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))
        
        # ------------- Create SBO ------------- #
        logger.info("Step 2 | Loading sbo and sbo_ancestors...")
        start_time = time.time()
        sbo_biodata_dir = self.get_param("biota:sbo_biodata_dir")
        SBO.create_sbo_db(sbo_biodata_dir, **params)
        len_sbo = SBO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))
        
        # ------------------- Create BTO ----------------- #
        logger.info("Step 3 | Loading bto and bto_ancestors...")
        start_time = time.time()
        bto_biodata_dir = self.get_param("biota:bto_biodata_dir")
        BTO.create_bto_db(bto_biodata_dir, **params)
        len_bto = BTO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))
        
        # ------------------- Create ECO ----------------- #
        logger.info("Step 4 | Loading eco and eco_ancestors...")
        start_time = time.time()
        eco_biodata_dir = self.get_param("biota:eco_biodata_dir")
        ECO.create_eco_db(eco_biodata_dir, **params)
        len_eco = ECO.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))
        
        # ------------- Create ChebiOntology ------------- #
        logger.info("Step 5 | Loading chebi ontology...")
        start_time = time.time()
        chebi_biodata_dir = self.get_param("biota:chebi_biodata_dir")
        ChebiOntology.create_chebi_ontology_db(chebi_biodata_dir, **params)
        len_chebi_ontology = ChebiOntology.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #chebi_ontology = {}".format(elapsed_time/60, len_chebi_ontology))

        # ---------------- Create Taxonomy --------------- #
        logger.info("Step 6 | Loading ncbi taxonomy...")
        start_time = time.time()
        ncbi_biodata_dir = self.get_param("biota:taxonomy_biodata_dir")
        Taxonomy.create_taxonomy_db(ncbi_biodata_dir, **params)
        len_taxonomy = Taxonomy.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))
        
        # ---------------- Create Compound --------------- #
        logger.info("Step 7 | Loading chebi compounds...")
        start_time = time.time()
        chebi_biodata_dir = self.get_param("biota:chebi_biodata_dir")
        Compound.create_compound_db(chebi_biodata_dir, **params)
        len_compound = Compound.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

        # ------------------ Create EnzymeFunction --------------- #
        logger.info("Step 8 | Loading brenda enzyme_functions and enzyme_btos...")
        start_time = time.time()
        brenda_biodata_dir = self.get_param("biota:brenda_biodata_dir")
        EnzymeFunction.create_enzyme_function_db(brenda_biodata_dir, **params)
        len_enzyme = EnzymeFunction.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #enzyme_functions = {} ".format(elapsed_time/60, len_enzyme))
        
        # ---------------- Create Reactions -------------- #
        logger.info("Step 9 | Loading rhea reactions...")
        start_time = time.time()
        rhea_biodata_dir = self.get_param("biota:rhea_biodata_dir")
        Reaction.create_reaction_db(rhea_biodata_dir, **params)
        len_rhea = Reaction.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))

        """"
        # ------------- Create EnzymeAnnotation ------------- #
        logger.info("Step 10 | Loading enzyme_function annotations...")
        start_time = time.time()
        EnzymeAnnotation.create_annotation_db()
        len_enzyme_annotation = EnzymeAnnotation.select().count()
        elapsed_time = time.time() - start_time
        logger.info("... done in {:10.2f} min for #enzyme_annotations = {}".format(elapsed_time/60, len_enzyme_annotation))
        """