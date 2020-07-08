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

from biota.sbo import SBO, SBOStandardJSONViewModel, SBOPremiumJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestGO
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")

class TestSBO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        SBO.drop_table()
        SBO.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #SBO.drop_table()
        pass
    
    def test_db_object(self):
        files = dict(
            sbo_data = "SBO_OBO.obo",
        )

        files_test = dict(
            sbo_data = "SBO_OBO_test.obo",
        )
    
        SBO.create_sbo(input_db_dir, **files_test)
        Controller.save_all()
        self.assertEqual(SBO.get(SBO.sbo_id == 'SBO:0000000').name, 'systems biology representation')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000005").name, 'obsolete mathematical expression')
        
        # --------- Testing views --------- #
        sbo1 = SBO.get(SBO.sbo_id == 'SBO:0000004')
        sbo1_standard_view_model = SBOStandardJSONViewModel(sbo1)
        sbo1_premium_view_model = SBOPremiumJSONViewModel(sbo1)
        view1 = sbo1_standard_view_model.render()
        view2 = sbo1_premium_view_model.render()
        print(view1)
        print(view2)
        self.assertEqual(view1,"""
            {
            "id": SBO:0000004,
            "name": modelling framework
            }
        """)
        self.assertEqual(view2,"""
            {
            "id": SBO:0000004,
            "name": modelling framework,
            "definition": Set of assumptions that underlay a mathematical description.,
            "ancestors": ['SBO:0000000']
            }
        """)
