import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.enzyme import Enzyme
from biota.db.protein import Protein

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Protein.drop_table()
        Enzyme.drop_table()
        Enzyme.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            brenda_file = "brenda_test.txt",
            bkms_file = "bkms_test.csv"
        )

        Enzyme.create_enzyme_db(**params)