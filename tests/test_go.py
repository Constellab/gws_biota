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
from onto.ontology import Onto
from gena.go import GO
from gena.sbo import SBO
from peewee import CharField, chunked
from manage import settings
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

############################################################################################
#
#                                        TestGO
#                                         
############################################################################################

path = settings.get_data("gena_db_path")

class TestGO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        GO.drop_table()
        GO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #GO.drop_table()
        pass
    
    def test_db_object(self):
        ### Test GO class ###
        onto_go = Onto.create_ontology_from_file(path, "go_test.obo")
        list_go = Onto.parse_obo_from_ontology(onto_go)
        test_go = GO.create_go(list_go)

        self.assertEqual(len(list_go), 9)
        self.assertEqual(list_go[0]['id'], 'GO:0000001')
        self.assertEqual(list_go[8]['name'], 'trans-hexaprenyltranstransferase activity')

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
