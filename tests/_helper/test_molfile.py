import sys
import os
import unittest

from gws.settings import Settings
from biota._helper.chebi import Chebi
import pybel

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_read_mol(self):
        settings = Settings.retrieve()
        testdata_path = os.path.join(
            settings.get_dir("biota:testdata_dir"),
            '../_helper/data/'
        )

        mol = Chebi.parse_csv_from_file(testdata_path,'structure.csv',delimiter=",")

        print(mol)
