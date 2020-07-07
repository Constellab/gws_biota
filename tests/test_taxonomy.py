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

from biota.taxonomy import Taxonomy, TaxonomyJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestTaxonomy
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")

class TestGO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        Taxonomy.drop_table()
        Taxonomy.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Taxonomy.drop_table()
        pass
    
    def test_db_object(self):
        Taxonomy.create_taxons_from_dict(['Homininae', 'Archaea'])
        Controller.save_all()
        #self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 41297).name, "Sphingomonadaceae")
        #tax1 = Taxonomy.get(Taxonomy.tax_id == 41297)
        #tax1_view_model = TaxonomyJSONViewModel(tax1)
        #view = tax1_view_model.render()
        #self.assertEqual(view, '{"tax_id": 41297 , "name": Sphingomonadaceae, "rank": family , "ancestors": [] }')