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
from biota.chebi_ontology import ChebiOntology
from biota.taxonomy import Taxonomy
from biota.compound import Compound
from biota.enzyme import Enzyme
from biota.reaction import Reaction

#import external module 
from biota.helper.rhea import Rhea
from biota.helper.brenda import Brenda
from biota.helper.ontology import Onto
from biota.helper.chebi import Chebi
from biota.helper.taxonomy import Taxo

#import Timer
from timeit import default_timer

############################################################################################
#
#                                        class test_main_taxonomy
#                                         
############################################################################################
settings = Settings.retrieve()
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

        start = default_timer()

        # ------------- Create Taxonomy ------------- #

        #Taxonomy.create_taxons_from_dict(['Archaea', 'Bacteria', 'Viruses'])
        #duration  = default_timer() - start
        #print("Part ['Archaea', 'Bacteria', 'Viruses'] of the taxonomy has been loaded in " + str(duration) + " sec")
        
        Taxonomy.create_taxons_from_dict(['Homininae'])
        duration  = default_timer() - start
        print("Part ['Eukaryota'] of the taxonomy has been loaded in " + str(duration) + " sec")