import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.pwo import PWO

settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")

class TestPWO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        PWO.drop_table()
        PWO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            pwo_file = "pwo_test.obo",
        )
    
        PWO.create_pwo_db(**params)
        self.assertEqual(PWO.get(PWO.pwo_id == 'PW:0000000').name, 'term zero')
        self.assertEqual(PWO.get(PWO.pwo_id == "PW:0000005").name, 'carbohydrate metabolic pathway')
