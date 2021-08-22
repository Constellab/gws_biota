import sys
import os
import unittest

from gws_core import Settings, GTest
from gws_biota import ECO

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")


class TestECO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GTest.drop_tables()
        GTest.create_tables()
        
    @classmethod
    def tearDownClass(cls):
        GTest.drop_tables()
    
    def test_db_object(self):
        GTest.print("ECO")
        params = dict(
            biodata_dir = testdata_path,
            eco_file = "eco_test.obo",
        )

        ECO.create_eco_db(**params)
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').get_name(), "inference from background scientific knowledge")
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000002').get_name(), "direct assay evidence")
