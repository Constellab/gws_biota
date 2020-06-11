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
from gena.taxonomy import Taxonomy
from peewee import CharField, chunked
from manage import settings

############################################################################################
#
#                                        TestTaxonomy
#                                         
############################################################################################


path = settings.get_data("gena_db_path")

class TestGO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        Taxonomy.drop_table()
        Taxonomy.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #GO.drop_table()
        pass
    
    def test_db_object(self):
        print('ok')
        Controller.save_all()
