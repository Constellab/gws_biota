import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.go import GO, GOJSONStandardViewModel, GOJSONPremiumViewModel

settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")

class TestGO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        GO.drop_table()
        GO.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        #GO.drop_table()
        pass
    
    def test_db_object(self):
        ### Test GO class ###
        files_test = dict(
            go_file = "go_test.obo",
        )

        GO.create_go_db(testdata_path, **files_test)
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').name, "mitochondrion inheritance")
       
        go1 = GO.get(GO.go_id == 'GO:0000006')
        go1_standard_view_model = GOJSONStandardViewModel(go1)
        go1_premium_view_model = GOJSONPremiumViewModel(go1)
        view1 = go1_standard_view_model.render()
        view2 = go1_premium_view_model.render()
        self.assertEqual(view1,"""
        {
            "id": "GO:0000006",
            "name": "high-affinity zinc transmembrane transporter activity"
        }
        """)
        self.assertEqual(view2,"""
        {
            "id": "GO:0000006",
            "name": "high-affinity zinc transmembrane transporter activity",
            "namespace": "molecular_function",
            "definition": "Enables the transfer of zinc ions (Zn2+) from one side of a membrane to the other, probably powered by proton motive force. In high-affinity transport the transporter is able to bind the solute even if it is only present at very low concentrations.",
            "ancestors": "['GO:0005385']"
        }
        """)