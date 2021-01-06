import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings

from biota.db.compound import Compound

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = os.path.join(
    settings.get_dir("biota:testdata_dir"),
    '../_helper/data/'
)

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Compound.create_table()
   
    @classmethod
    def tearDownClass(cls):
        Compound.drop_table()
        pass

    def test_db_object(self):

        params = dict(
            biodata_dir = testdata_path,
            chebi_file = "chebi_test.obo",
        )

        Compound.create_compound_db(**params)
        self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:24431').get_name(), "chemical entity")
        self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:17051').get_name(), 'fluoride')
        
        comp = Compound.get(Compound.chebi_id == 'CHEBI:49499')
        self.assertEqual(comp.get_name(), 'beryllium difluoride')
        
        self.assertEqual(len(comp.ancestors), 1)
        self.assertEqual(comp.ancestors[0].get_name(), 'fluoride salt')