import sys
import os
import unittest
 
from biota._helper.ontology import Onto
from gws.settings import Settings
import json

############################################################################################
#
#                                        Test go.obo parser
#                                         
############################################################################################


class TestOntology(unittest.TestCase):
    def test_db_object(self):
        settings = Settings.retrieve()
        go_path = settings.get_data("go_test_data_dir")
        eco_path = settings.get_data("eco_test_data_dir")
        bto_path = settings.get_data("bto_test_data_dir")
        sbo_path = settings.get_data("sbo_test_data_dir")
        
        #### Test go parser ####
        ontology = Onto.create_ontology_from_obo(go_path,'go_test.obo')
        list_go = Onto.parse_obo_from_ontology(ontology)
        self.assertEqual(len(list_go), 14)
        self.assertEqual(list_go[0]['id'], 'GO:0000001')
        self.assertEqual(list_go[1]['id'], 'GO:0000002')
        self.assertEqual(len(list_go[9]['ancestors']), 2)
        
        #### Test sbo parser ####
        file = "sbo_test.obo"
        Onto.correction_of_sbo_file(sbo_path, file, 'sbo_out_test.obo')
        ontology = Onto.create_ontology_from_owl(sbo_path, 'sbo_out_test.obo')
        list_sbo_terms = Onto.parse_sbo_terms_from_ontology(ontology)
        self.assertEqual(len(list_sbo_terms), 21)
        self.assertEqual(list_sbo_terms[0]['id'], 'SBO:0000000')

        
        #### Test BTO parser ####
        file = "bto_test.json"
        list_bto = Onto.parse_bto_from_json(bto_path, file)
        self.assertEqual(len(list_bto), 18)
        self.assertEqual(list_bto[0], {'id': 'BTO_0000000', 'label': 'tissues, cell types and enzyme sources', 'ancestors': ['BTO_0000000']})
        self.assertEqual(list_bto[1], {'id': 'BTO_0000001', 'label': 'culture condition:-induced cell', 'ancestors': ['BTO_0000001', 'BTO_0000216']})
        
        #### Test ECO parser ####
        file = "eco_test.obo"
        ontology = Onto.create_ontology_from_obo(eco_path, file)
        list_eco = Onto.parse_eco_terms_from_ontoloy(ontology)