import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.pwo import PWO

settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")

class TestPWO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        PWO.drop_table()
        PWO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_db_object(self):
        files_test = dict(
            pwo_data = "pwo_test.obo",
        )
    
        PWO.create_pwo_db(test_data_path, **files_test)
        self.assertEqual(PWO.get(PWO.pwo_id == 'PW:0000000').name, 'term zero')
        self.assertEqual(PWO.get(PWO.pwo_id == "PW:0000005").name, 'carbohydrate metabolic pathway')
