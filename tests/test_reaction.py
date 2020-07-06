import sys
import os
import unittest
import copy
import asyncio

from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Resource
from gws.prism.controller import Controller

from peewee import CharField, ForeignKeyField, chunked
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from biota.reaction import Reaction, ReactionJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestReaction
#
############################################################################################

input_db_dir = settings.get_data("biota_db_path")



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

        Reaction.create_reactions_from_files(input_db_dir, **files_test)
        #self.assertEqual(Reaction.get(Reaction.source_accession == 'RHEA:10022').biocyc_ids, 'RXN3O-127')
        #self.assertEqual(Reaction.get(Reaction.source_accession == 'RHEA:10031').kegg_id, 'R00279')
        rea1 = Reaction.get(Reaction.source_accession == 'RHEA:10031')
        q = rea1.substrates
        for i in range(0, len(q)):
            print(q[i].data)
        
        #rea1_view_model = ReactionJSONViewModel(rea1)
        #view = rea1_view_model.render()
        #print(view)
        #self.assertEqual(view, '{"source_accession": RHEA:10031 , "direction": BI, "master_id": 10028 , "biocyc_id": None, "kegg_id": R00279 }')