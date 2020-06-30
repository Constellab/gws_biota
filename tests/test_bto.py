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


from biota.bto import BTO, BTOJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestBTO
#                                         
############################################################################################
input_db_dir = settings.get_data("biota_db_path")
 
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

        BTO.create_bto(input_db_dir, **files_test)
        Controller.save_all()
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')
        bto1 = BTO.get(BTO.bto_id == 'BTO_0000000')
        bto1_view_model = BTOJSONViewModel(bto1)
        Controller.save_all()
        view = bto1_view_model.render()
        print(view)
        #self.assertEqual(view, )
        
