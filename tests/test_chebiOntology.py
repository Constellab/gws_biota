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

from biota.chebiOntology import ChebiOntology, ChebiOntologyJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")

class TestChebiOntology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ChebiOntology.drop_table()
        ChebiOntology.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            chebi_data = "chebi.obo",
        )

        files_test = dict(
            chebi_data = "chebi_test.obo",
        )
        
        ChebiOntology.create_chebis(input_db_dir, **files_test)
        Controller.save_all()
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        chebi1 = ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431')
        chebi1_view_model = ChebiOntologyJSONViewModel(chebi1)
        view = chebi1_view_model.render()
        self.assertEqual(view, '{"chebi_id": CHEBI:24431 , "name": chemical entity, "definition": A chemical entity is a physical entity of interest in chemistry including molecular entities, parts thereof, and chemical substances. }')