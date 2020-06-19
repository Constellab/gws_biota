import sys
import os
import unittest

from peewee import CharField, chunked
from gws.prism.model import Model, ViewModel, ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller

from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from gena.go import GO
from manage import settings

############################################################################################
#
#                                        TestGO
#                                         
############################################################################################

input_db_dir = settings.get_data("gena_db_path")

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
        files = dict(
            go_data = "go.obo",
        )

        files_test = dict(
            go_data = "go_test.obo",
        )

        GO.create_go(input_db_dir, **files_test)
        Controller.save_all()
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').name, "mitochondrion inheritance")