import sys
import os
import unittest

from gws.settings import Settings
from biota._helper.chebi import Chebi

import ctfile


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
        return
        settings = Settings.retrieve()
        testdata_path = os.path.join(settings.get_dir("biota:testdata_dir"), 'chebi.sdf')

        with open(testdata_path, 'r') as f:
            ctf = ctfile.load(f)

            #print(ctf.molfiles[0].atoms)
            print(ctf.molfiles[0].atoms[0])
            print(ctf.molfiles[0].bonds[0])

            self.assertEqual(ctf.molfiles[0].atoms[0].x, "-2.8644")
            self.assertEqual(ctf.molfiles[0].atoms[0].y, "-0.2905")
            self.assertEqual(ctf.molfiles[0].atoms[0].atom_symbol, "C")

            print(ctf.sdfdata[0])
