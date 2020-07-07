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

from biota.eco import ECO, ECOJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestECO
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")


class TestECO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        ECO.drop_table()
        ECOJSONViewModel.drop_table()
        ECO.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        #ECO.drop_table()
        pass
    
    def test_db_object(self):
        ### Test ECO class ###
        files = dict(
            eco_data = "eco.obo",
        )

        files_test = dict(
            eco_data = "eco_test.obo",
        )

        ECO.create_eco(input_db_dir, **files_test)
        Controller.save_all()
        #self.assertEqual(GO.get(GO.go_id == 'GO:0000001').name, "mitochondrion inheritance")
        #go1 = GO.get(GO.go_id == 'GO:0000001')
        #go1_view_model = GOJSONViewModel(go1)
        #Controller.save_all()
        #view = go1_view_model.render()
        #self.assertEqual(view, '{"id": GO:0000001 , "name": mitochondrion inheritance, "namespace": biological_process , "definition": The distribution of mitochondria, including the mitochondrial genome, into daughter cells after mitosis or meiosis, mediated by interactions between mitochondria and the cytoskeleton. }')