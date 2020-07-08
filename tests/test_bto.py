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


from biota.bto import BTO, BTOAncestor, BTOJSONStandardViewModel, BTOJSONPremiumViewModel
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
        # --------- Testing views --------- #
        bto1 = BTO.get(BTO.bto_id == 'BTO_0000002')
        bto1_standard_view_model = BTOJSONStandardViewModel(bto1)
        bto1_premium_view_model = BTOJSONPremiumViewModel(bto1)
        view1 = bto1_standard_view_model.render()
        view2 = bto1_premium_view_model.render()
        self.assertEqual(view1,"""
            {
            "id": BTO_0000002, 
            "label": culture condition:1,4-dichlorobenzene-grown cell,
            }
        """)
        self.assertEqual(view2,"""
            {
            "id": BTO_0000002, 
            "label": culture condition:1,4-dichlorobenzene-grown cell,
            "ancestors" : ['BTO_0000216', 'BTO_0001479'],
            }
        """)
        
