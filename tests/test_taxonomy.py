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

from biota.taxonomy import Taxonomy, TaxonomyJSONStandardViewModel, TaxonomyJSONPremiumViewModel
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
        Taxonomy.create_taxons_from_dict(['Homininae'])
        #self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 9593).name, "Gorilla gorilla")
        
        # --------- Testing views --------- #
        tax1 = Taxonomy.get(Taxonomy.tax_id == 9593)
        
        tax1_standard_view_model = TaxonomyJSONStandardViewModel(tax1)
        tax1_premium_view_model = TaxonomyJSONPremiumViewModel(tax1)
        
        view1 = tax1_standard_view_model.render()
        view2 = tax1_premium_view_model.render()

        self.assertEqual(view1,"""
            {
            "id": 9593,
            "name": Gorilla gorilla,
            }
        """)

        self.assertEqual(view2,"""
            {
            "id": 9593,
            "name": Gorilla gorilla,
            "rank": species,
            "ancestor": 9592,
            }
        """)