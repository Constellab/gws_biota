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

from gena.taxonomy import Taxonomy
from manage import settings

############################################################################################
#
#                                        TestTaxonomy
#                                         
############################################################################################

input_db_dir = settings.get_data("gena_db_path")

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
        Taxonomy.create_taxons_from_list('Sphingomonadaceae')
        Controller.save_all()
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 579138).name, "Zymomonas mobilis subsp. pomaceae ATCC 29192")
