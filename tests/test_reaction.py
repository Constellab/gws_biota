import unittest
import copy
from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Resource
from gws.prism.controller import Controller

import sys
import os
import unittest

import asyncio

from peewee import CharField, ForeignKeyField
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from gws.prism.controller import Controller
from rhea.rhea import Rhea
from gena.reaction import Reaction
from peewee import CharField, chunked
from manage import settings

path = settings.get_data("gena_db_path")

class TestReaction(unittest.TestCase):

    def setUp(cls):
        Reaction.drop_table()
        Reaction.create_table()
        pass


    @classmethod
    def setUpClass(cls):
        Reaction.drop_table()
        Reaction.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass
    
    def test_db_object(self):
        list_react = Rhea.parse_reaction_from_file(path, 'rhea-kegg-test.reaction')
        Reaction.create_reactions(list_react)
        #test_dict = Reaction.test_json(self, r)
        Controller.save_all()

        list_directions = Rhea.parse_csv_from_file(path, 'rhea-directions-test.tsv')
        list_master, list_LR, list_RL, list_BI = Rhea.get_columns_from_lines(list_directions)

        Reaction.set_direction_from_list(list_master, 'UN')
        Reaction.set_direction_from_list(list_LR, 'LR')
        Reaction.set_direction_from_list(list_RL, 'RL')
        Reaction.set_direction_from_list(list_BI, 'BI')
        Controller.save_all()

        list_ecocyc_react = Rhea.parse_csv_from_file(path, 'rhea2ecocyc-test.tsv')
        list_macie_react = Rhea.parse_csv_from_file(path, 'rhea2macie_test.tsv')
        list_metacyc_react = Rhea.parse_csv_from_file(path, 'rhea2metacyc-test.tsv')

        Reaction.get_master_and_id(list_ecocyc_react)
        Reaction.get_master_and_id(list_macie_react)
        Reaction.get_master_and_id(list_metacyc_react)

        Controller.save_all()


        list_kegg_react = Rhea.parse_csv_from_file(path, 'rhea2kegg_reaction_test.tsv')
        list_ec_react = Rhea.parse_csv_from_file(path, 'rhea2ec-test.tsv')

        Reaction.get_master_and_id_from_rhea2kegg(list_kegg_react)
        Reaction.get_master_and_id_from_rhea2ec(list_ec_react)
        
        Controller.save_all()
