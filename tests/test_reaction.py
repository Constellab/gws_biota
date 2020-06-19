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

from gena.reaction import Reaction
from manage import settings

############################################################################################
#
#                                        TestReaction
#
############################################################################################

input_db_dir = settings.get_data("gena_db_path")
substrate_reaction = Reaction.substrates.get_through_model()
product_reaction = Reaction.products.get_through_model()
enzyme_reaction = Reaction.enzymes.get_through_model()

class TestReaction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Reaction.drop_table()
        Reaction.create_table()
        #reactions_compounds_through.drop_table()
        substrate_reaction.drop_table()
        product_reaction.drop_table()
        enzyme_reaction.drop_table()
        substrate_reaction.create_table()
        product_reaction.create_table()
        enzyme_reaction.create_table()
        
        
   
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
            rhea2ec_file = 'rhea2ec.tsv'
        )

        files_test = dict(
            rhea_kegg_reaction_file =  'rhea-kegg_test.reaction',
            rhea_direction_file = 'rhea-directions-test.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc-test.tsv',
            rhea2metacyc_file = 'rhea2metacyc-test.tsv',
            rhea2macie_file = 'rhea2macie_test.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction_test.tsv',
            rhea2ec_file = 'rhea2ec-test.tsv'
        )

        Reaction.create_reactions_from_files(input_db_dir, **files_test)
        self.assertEqual(Reaction.get(Reaction.source_accession == 'RHEA:10022').biocyc_id, 'RXN3O-127')
        self.assertEqual(Reaction.get(Reaction.source_accession == 'RHEA:10031').kegg_id, 'R00279')