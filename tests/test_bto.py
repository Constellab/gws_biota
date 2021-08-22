import sys
import os
import unittest

from gws_core import Settings, GTest
from gws_biota import BTO

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")
 
class TestBTO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        GTest.drop_tables()
        GTest.create_tables()
        
    @classmethod
    def tearDownClass(cls):
        GTest.drop_tables()
    
 
    def test_db_object(self):
        GTest.print("BTO")
        params = dict(
            biodata_dir = testdata_path,
            bto_file = "bto_test.json",
        )

        BTO.create_bto_db(**params)
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').get_name(), 'tissues, cell types and enzyme sources')        
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000002').get_name(), 'culture condition:1,4-dichlorobenzene-grown cell')