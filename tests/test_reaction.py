import sys
import os
import unittest
import copy
import asyncio

from gws.settings import Settings
from biota.reaction import Reaction, ReactionJSONStandardViewModel, ReactionJSONPremiumViewModel

############################################################################################
#
#                                        TestReaction
#
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_path")

files_model = dict(
    substrate_reaction = Reaction.substrates.get_through_model(),
    product_reaction = Reaction.products.get_through_model(),
    enzyme_reaction = Reaction.enzymes.get_through_model()
    )

class TestReaction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Reaction.drop_table(**files_model)
        Reaction.create_table(**files_model)
        
   
    @classmethod
    def tearDownClass(cls):
        #Reaction.drop_table()
        pass
    
    def test_db_object(self):
        files = dict(
            rhea_kegg_reaction_file =  'rhea-kegg.reaction',
            rhea_direction_file = 'rhea-directions.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc.tsv',
            rhea2metacyc_file = 'rhea2metacyc.tsv',
            rhea2macie_file = 'rhea2macie.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction.tsv',
            rhea2ec_file = 'rhea2ec.tsv',
            rhea2reactome_file = 'rhea2reactome.tsv'
        )

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

        Reaction.create_reactions_from_files(test_data_path, **files_test)
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
            "enzymes": None,
            "substrates": ['CHEBI:29986', 'CHEBI:15377', 'CHEBI:15379'],
            "products": ['CHEBI:16810', 'CHEBI:16240', 'CHEBI:28938']
            }
        """)
