import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.bto import BTO

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")
 
class TestBTO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        BTO.drop_table()
        BTO.create_table()

   
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            bto_file = "bto_test.json",
        )

        BTO.create_bto_db(**params)
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')        
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000002').label, 'culture condition:1,4-dichlorobenzene-grown cell')