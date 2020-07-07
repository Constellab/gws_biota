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

from manage import settings
from biota.enzyme import Enzyme, EnzymeJSONViewModel
from biota.bto import BTO

############################################################################################
#
#                                        TestEnzymes
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")
enzyme_bto = Enzyme.bto.get_through_model()

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Enzyme.create_table()
        enzyme_bto.drop_table()
        enzyme_bto.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Enzyme.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            brenda_file = "brenda_download_20200504.txt"
        )

        files_test = dict(
            brenda_file = "brenda_test.txt"
        )
        Enzyme.create_enzymes_from_dict(input_db_dir, **files_test)
        Controller.save_all()
        self.assertEqual(Enzyme.get(Enzyme.ec == '1.4.3.7').organism, 'Candida boidinii')
        self.assertEqual(Enzyme.get(Enzyme.ec == '3.5.1.43').organism, 'Bacillus circulans')
        enz1 = Enzyme.get(Enzyme.ec == '3.5.1.43')
        enz1_view_model = EnzymeJSONViewModel(enz1)
        view = enz1_view_model.render()