import json
import unittest
from biota._helper.ontology import Onto
from gws.settings import Settings

class TestOntology(unittest.TestCase):
    
    def test_db_object(self):
        
        settings = Settings.retrieve()
        go_path = settings.get_data("biota:go_testdata_dir")
        eco_path = settings.get_data("biota:eco_testdata_dir")
        bto_path = settings.get_data("biota:bto_testdata_dir")
        sbo_path = settings.get_data("biota:sbo_testdata_dir")
        pwo_path = settings.get_data("biota:pwo_testdata_dir")
        
        #### Test go parser ####
        ontology = Onto.create_ontology_from_obo(go_path,'go_test.obo')
        list_go = Onto.parse_obo_from_ontology(ontology)
        self.assertEqual(len(list_go), 14)
        self.assertEqual(list_go[0]['id'], 'GO:0000001')
        self.assertEqual(list_go[1]['id'], 'GO:0000002')
        self.assertEqual(len(list_go[9]['ancestors']), 2)
        
        #### Test sbo parser ####
        file = "sbo_test.obo"
        Onto.correction_of_sbo_file(sbo_path, file, 'sbo_corrected.obo')
        ontology = Onto.create_ontology_from_obo(sbo_path, 'sbo_corrected.obo')
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
        self.assertEqual(len(list_eco), 25)
        self.assertEqual(list_eco[0], {'id': 'ECO:0000000', 'name': 'evidence', 'definition': 'A type of information that is used to support an assertion.'})
        self.assertEqual(list_eco[10], {'id': 'ECO:0000010', 'name': 'protein expression evidence', 'definition': 'A type of expression pattern evidence resulting from protein abundance quantification techniques.', 'ancestors': ['ECO:0000008']})
      
        #### Test pwo parser ####
        file = "pwo_test.obo"
        Onto.correction_of_pwo_file(pwo_path, file, 'pwo_out_test.obo')
        ontology = Onto.create_ontology_from_obo(pwo_path, 'pwo_out_test.obo')
        list_pwo = Onto.parse_pwo_terms_from_ontology(ontology)
        self.assertEqual(len(list_pwo), 34)
        self.assertEqual(list_pwo[0], {'id': 'PW:0000000', 'name': 'term zero', 'definition': 'None'})
        self.assertEqual(list_pwo[10], {'id': 'PW:0000010', 'name': 'lipid metabolic pathway', 'definition': 'The metabolic reactions involved in the oxidation, utilization and/or synthesis of lipids in the tissues.', 'ancestors': ['PW:0000002']})
      