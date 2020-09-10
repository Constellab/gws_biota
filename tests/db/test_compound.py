import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.compound import Compound

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Compound.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            chebi_compound_file = "compounds_test.tsv",
            chebi_chemical_data_file =  "chemical_data_test.tsv",
        )

        Compound.create_compound_db(**params)
        self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:58321').name, 'L-allysine zwitterion')
        self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:59789').name, 'S-adenosyl-L-methionine zwitterion')
