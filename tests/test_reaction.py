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
from rhea.reaction_parser import parser_reaction_from_file
from hello.reaction import Reaction
from peewee import CharField, chunked

path = os.path.realpath('./databases_input')
class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Reaction.drop_table()
        Reaction.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass
    
    def test_db_object(self):
        list_react = parser_reaction_from_file(path, 'rhea-kegg.reaction')
        Reaction.create_reactions(self, list_react)


        Controller.save_all()
        async def app(scope, receive, send):
            assert scope['type'] == 'http'
            request = Request(scope, receive)
            vm = await Controller.action(request)
            html = vm.render()
            response = HTMLResponse(html)
            await response(scope, receive, send)

        Controller.is_query_params = True
        client = TestClient(app)
