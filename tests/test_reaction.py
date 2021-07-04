import sys
import os
import unittest
import copy
import asyncio

from gws.settings import Settings
from biota.reaction import Reaction
from biota.compound import Compound
from biota.enzyme import Enzyme

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestReaction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Reaction.drop_table()
        Enzyme.drop_table()
        Compound.drop_table()
        
        Reaction.create_table()
        Enzyme.create_table()
        Compound.create_table()
        
    @classmethod
    def tearDownClass(cls):
        Reaction.drop_table()
        Compound.drop_table()
        Enzyme.drop_table()
        pass
    
    def test_db_object(self):

        params = dict(
            biodata_dir = testdata_path,
            rhea_reaction_file =  'rhea-reactions_test.txt',
            rhea_direction_file = 'rhea-directions-test.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc-test.tsv',
            rhea2metacyc_file = 'rhea2metacyc-test.tsv',
            rhea2macie_file = 'rhea2macie_test.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction_test.tsv',
            rhea2ec_file = 'rhea2ec-test.tsv',
            rhea2reactome_file = 'rhea2reactome_test.tsv'
        )

        Reaction.create_reaction_db(**params)
        self.assertEqual(Reaction.get(Reaction.rhea_id == 'RHEA:10022').master_id, '10020')
        self.assertEqual(Reaction.get(Reaction.rhea_id == 'RHEA:10031').kegg_id, 'R00279')