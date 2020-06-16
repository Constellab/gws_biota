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
from gena.bto import BTO
from peewee import CharField, chunked
from manage import settings
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

############################################################################################
#
#                                        TestBTO
#                                         
############################################################################################
input_db_dir = settings.get_data("gena_db_path")


class TestBTO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        BTO.drop_table()
        BTO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #BTO.drop_table()
        pass
    
    def test_db_object(self):
        ### Test GO class ###

        files = dict(
            bto_json_data = "bto.json",
        )

        files_test = dict(
            bto_json_data = "bto_test.json",
        )

        BTO.create_bto(input_db_dir, **files)
        """
        self.assertEqual(len(list_go), 9)
        self.assertEqual(list_go[0]['id'], 'GO:0000001')
        self.assertEqual(list_go[8]['name'], 'trans-hexaprenyltranstransferase activity')
        """
        Controller.save_all()
