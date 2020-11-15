import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.go import GO

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestGO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        GO.drop_table()
        GO.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        GO.drop_table()
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            go_file = "go_test.obo",
        )

        GO.create_go_db(**params)
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').get_name(), "mitochondrion inheritance")
        self.assertEqual(GO.get(GO.go_id == 'GO:0000006').get_name(), "high-affinity zinc transmembrane transporter activity")
