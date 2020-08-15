import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.eco import ECO

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
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            eco_file = "eco_test.obo",
        )

        ECO.create_eco_db(**params)
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').name, "inference from background scientific knowledge")
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000002').name, "direct assay evidence")
