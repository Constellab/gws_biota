import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.sbo import SBO

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestSBO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        SBO.drop_table()
        SBO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        SBO.drop_table()
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            sbo_file = "sbo_test.obo",
        )
    
        SBO.create_sbo_db(**params)
        self.assertEqual(SBO.get(SBO.sbo_id == 'SBO:0000000').get_name(), 'systems biology representation')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000005").get_name(), 'obsolete mathematical expression')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000004").get_name(), 'modelling framework')

