import sys
import os
import unittest

from peewee import CharField, chunked
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate

from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from biota.pathway import Pathway, PathwayJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")


class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Pathway.drop_table()
        Pathway.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Pathway.drop_table()
        pass

    def test_db_object(self):
        print('test is ok')