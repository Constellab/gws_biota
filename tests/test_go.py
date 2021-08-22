import sys
import os
import unittest

from gws_core import Settings, GTest
from gws_biota import GO

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestGO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        GTest.drop_tables()
        GTest.create_tables()
        
    @classmethod
    def tearDownClass(cls):
        GTest.drop_tables()
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            go_file = "go_test.obo",
        )
        GO.create_go_db(**params)
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').get_name(), "mitochondrion inheritance")
        self.assertEqual(GO.get(GO.go_id == 'GO:0000006').get_name(), "high-affinity zinc transmembrane transporter activity")
