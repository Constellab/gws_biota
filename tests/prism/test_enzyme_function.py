import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.db.enzyme import Enzyme
from biota.db.protein import Protein
from biota.db.enzyme_function import EnzymeFunction

settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Protein.drop_table()
        EnzymeFunction.drop_table()
        EnzymeFunction.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        files_test = dict(
            brenda_file = "brenda_test.txt"
        )

        EnzymeFunction.create_enzyme_function_db(test_data_path, **files_test)

        enzo = EnzymeFunction.select().join(Enzyme).where(Enzyme.ec == '1.4.3.7')
        self.assertEqual(enzo[0].organism, 'Candida boidinii')

        enzo = EnzymeFunction.select().join(Enzyme).where(Enzyme.ec == '3.5.1.43')
        self.assertEqual(enzo[0].organism, 'Bacillus circulans')