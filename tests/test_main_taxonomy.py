import sys
import os
import unittest
import copy
import asyncio

#import from biota
from gws.settings import Settings
from biota.go import GO
from biota.sbo import SBO
from biota.bto import BTO
from biota.chebiOntology import ChebiOntology
from biota.taxonomy import Taxonomy
from biota.compound import Compound
from biota.enzyme import Enzyme
from biota.reaction import Reaction

#import external module 
from rhea.rhea import Rhea
from brenda.brenda import Brenda
from onto.ontology import Onto
from chebi.chebi import Chebi
from taxo.taxonomy import Taxo

#import Timer
from timeit import default_timer

############################################################################################
#
#                                        class test_main_taxonomy
#                                         
############################################################################################
settings = Settings.retrieve()
input_db_dir = settings.get_data("biota_input_db_path")

class TestMain(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        # --- drops --- #
        Taxonomy.drop_table()
        # --- creations --- #
        Taxonomy.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_db_object(self):
        files = dict(
            go_data = "go.obo",
            sbo_data = "SBO_OBO.obo",
            chebi_data = "chebi.obo",
            bto_json_data = "bto.json",
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file =  "chemical_data.tsv",
            brenda_file = "brenda_download_20200504.txt",
            rhea_kegg_reaction_file =  'rhea-kegg.reaction',
            rhea_direction_file = 'rhea-directions.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc.tsv',
            rhea2metacyc_file = 'rhea2metacyc.tsv',
            rhea2macie_file = 'rhea2macie.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction.tsv',
            rhea2ec_file = 'rhea2ec.tsv'
        )

        start = default_timer()

        # ------------- Create Taxonomy ------------- #
        #Taxonomy.create_taxons_from_dict(['Archaea', 'Bacteria', 'Viruses'])
        #duration  = default_timer() - start
        #print("Part ['Archaea', 'Bacteria', 'Viruses'] of the taxonomy has been loaded in " + str(duration) + " sec")
        Taxonomy.create_taxons_from_dict(['Eukaryota'])
        duration  = default_timer() - start
        print("Part ['Eukaryota'] of the taxonomy has been loaded in " + str(duration) + " sec")