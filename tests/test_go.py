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

from biota.go import GO, GOJSONStandardViewModel, GOJSONPremiumViewModel
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
        GOJSONStandardViewModel.drop_table()
        GO.create_table()
        GOJSONStandardViewModel.create_table()
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
        # --------- Testing views --------- #
        go1 = GO.get(GO.go_id == 'GO:0000006')
        go1_standard_view_model = GOJSONStandardViewModel(go1)
        go1_premium_view_model = GOJSONPremiumViewModel(go1)
        view1 = go1_standard_view_model.render()
        view2 = go1_premium_view_model.render()
        self.assertEqual(view1,"""
            {
            "id": GO:0000006,
            "name": high-affinity zinc transmembrane transporter activity
            }
        """)
        self.assertEqual(view2,"""
            {
            "id": GO:0000006,
            "name": high-affinity zinc transmembrane transporter activity,
            "namespace": molecular_function,
            "definition": Enables the transfer of zinc ions (Zn2+) from one side of a membrane to the other, probably powered by proton motive force. In high-affinity transport the transporter is able to bind the solute even if it is only present at very low concentrations.,
            "ancestors": ['GO:0005385']
            }
        """)