import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.bto import BTO, BTOJSONViewModel

settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")
 
class TestBTO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        BTO.drop_table()
        BTO.create_table()

   
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_db_object(self):
        files_test = dict(
            bto_json_data = "bto_test.json",
        )

        BTO.create_bto_db(testdata_path, **files_test)
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')
        
        bto = BTO.get(BTO.bto_id == 'BTO_0000002')
        bto_view_model = BTOJSONViewModel(bto)
        view = bto_view_model.render()
        self.assertEqual(view,'{"id": "BTO_0000002", "label": "culture condition:1,4-dichlorobenzene-grown cell"}')
