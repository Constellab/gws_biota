import sys
import os
import unittest
import copy
import asyncio

from gws.settings import Settings
from biota.db.reaction import Reaction, ReactionJSONStandardViewModel, ReactionJSONPremiumViewModel

############################################################################################
#
#                                        TestReaction
#
############################################################################################
settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")

class TestReaction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Reaction.drop_table()
        Reaction.create_table()
        
   
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_db_object(self):

        files_test = dict(
            rhea_kegg_reaction_file =  'rhea-kegg_test.reaction',
            rhea_direction_file = 'rhea-directions-test.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc-test.tsv',
            rhea2metacyc_file = 'rhea2metacyc-test.tsv',
            rhea2macie_file = 'rhea2macie_test.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction_test.tsv',
            rhea2ec_file = 'rhea2ec-test.tsv',
            rhea2reactome_file = 'rhea2reactome_test.tsv'
        )

        Reaction.create_reaction_db(testdata_path, **files_test)
        self.assertEqual(Reaction.get(Reaction.source_accession == 'RHEA:10022').master_id, '10020')
        self.assertEqual(Reaction.get(Reaction.source_accession == 'RHEA:10031').kegg_id, 'R00279')
        
        # --------- Testing views --------- #
        rea1 = Reaction.get(Reaction.source_accession == 'RHEA:10031')
        
        rea1_standard_view_model = ReactionJSONStandardViewModel(rea1)
        rea1_premium_view_model = ReactionJSONPremiumViewModel(rea1)
        
        view1 = rea1_standard_view_model.render()
        view2 = rea1_premium_view_model.render()

        self.assertEqual(view1,"""
            {
            "id": RHEA:10031,
            "definition": D-glutamate + H2O + O2 <=> 2-oxoglutarate + H2O2 + NH4(+),
            }
        """)
        
        self.assertEqual(view2,"""
            {
            "id": RHEA:10031,
            "definition": D-glutamate + H2O + O2 <=> 2-oxoglutarate + H2O2 + NH4(+),
            "equation": CHEBI:29986 + CHEBI:15377 + CHEBI:15379 <=> CHEBI:16810 + CHEBI:16240 + CHEBI:28938,
            "master_id": 10028,
            "direction" : BI,
            "enzyme_functions": None,
            "substrates": ['CHEBI:29986', 'CHEBI:15377', 'CHEBI:15379'],
            "products": ['CHEBI:16810', 'CHEBI:16240', 'CHEBI:28938']
            }
        """)
