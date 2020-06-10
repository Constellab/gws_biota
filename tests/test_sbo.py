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

class TestSBO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        SBO.drop_table()
        SBO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #GO.drop_table()
        pass
    
    def test_db_object(self):
        onto_sbo = Onto.create_ontology_from_owl(path, "SBO_OWL_test.owl")
        list_sbo = Onto.parse_terms_from_ontology(onto_sbo)
        test_sbo = SBO.create_sbo(list_sbo)

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
