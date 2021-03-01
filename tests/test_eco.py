import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.eco import ECO

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")


class TestECO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        ECO.drop_table()
        ECO.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        ECO.drop_table()
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            eco_file = "eco_test.obo",
        )

        ECO.create_eco_db(**params)
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').get_name(), "inference from background scientific knowledge")
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000002').get_name(), "direct assay evidence")
