import sys
import os
import unittest
import copy
import asyncio

#import from biota
from gws.settings import Settings
from biota.prism.go import GO
from biota.prism.sbo import SBO
from biota.prism.bto import BTO
from biota.prism.chebi_ontology import ChebiOntology
from biota.prism.taxonomy import Taxonomy
from biota.prism.compound import Compound
from biota.prism.enzyme import Enzyme
from biota.prism.reaction import Reaction

#import external module 
from biota.prism.helper.rhea import Rhea
from biota.prism.helper.brenda import Brenda
from biota.prism.helper.ontology import Onto
from biota.prism.helper.chebi import Chebi
from biota.prism.helper.taxonomy import Taxo

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