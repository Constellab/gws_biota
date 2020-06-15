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
from peewee import CharField, chunked

from chebi.chebi import Chebi
from gena.chebi_ontology import Chebi_Ontology
from manage import settings
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################

input_db_dir = settings.get_data("gena_db_path")

class TestCompound(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        Chebi_Ontology.drop_table()
        Chebi_Ontology.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            chebi_data = "chebi.obo",
        )

        files_test = dict(
            chebi_data = "chebi_test.obo",
        )

        Chebi_Ontology.create_chebis(input_db_dir, **files_test)
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