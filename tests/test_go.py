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

from biota.go import GO, GOJSONViewModel, GOViewer
from manage import settings

############################################################################################
#
#                                        TestGO
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")

class TestGO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        GO.drop_table()
        GOJSONViewModel.drop_table()
        GO.create_table()
        pass
   
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
        go1 = GO.get(GO.go_id == 'GO:0000001')
        p1 = GOViewer()
        p1.input['GO'] = go1
        params = {'view_type': 'standard'}
        p1.run(params)
        view = s1.output['GOJSONView'].render()
        #go1 = GO.get(GO.go_id == 'GO:0000001')
        #go1_view_model = GOJSONViewModel(go1)
        #Controller.save_all()
        #view = go1_view_model.render()
        #self.assertEqual(view, '{"id": GO:0000001 , "name": mitochondrion inheritance, "namespace": biological_process , "definition": The distribution of mitochondria, including the mitochondrial genome, into daughter cells after mitosis or meiosis, mediated by interactions between mitochondria and the cytoskeleton. }')