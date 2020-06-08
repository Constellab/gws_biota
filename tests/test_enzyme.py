import sys
import os
import unittest


from peewee import CharField
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from manage import settings
from peewee import CharField, chunked
from brenda.brenda_parser import create_brenda, parse_all_proteins_for_all_ecs
from gena.enzyme import Enzyme

import logging
from collections import OrderedDict
from brendapy import BrendaParser, BrendaProtein
from brendapy.taxonomy import Taxonomy

from brendapy import utils
from brendapy.taxonomy import Taxonomy
from brendapy.tissues import BTO
from brendapy.substances import CHEBI


############################################################################################
#
#                                        TestEnzymes
#                                         
############################################################################################

path = settings.get_data("gena_db_path")

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Enzyme.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Enzyme.drop_table()
        pass

    def test_db_object(self):
        file = "brenda_download.txt"
        brenda = create_brenda(path,file)
        list_ = parse_all_proteins_for_all_ecs()
        Enzyme.create_enzymes(self, list_)
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