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


from biota.compound import Compound, CompoundHTMLViewModel, CompoundJSONViewModel
from manage import settings

############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################
#path = os.path.realpath('./databases_input') #Set the path where we can find input data
input_db_dir = settings.get_data("biota_db_path")

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Compound.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file =  "chemical_data.tsv",
            #rhea_kegg_compound_file =  "rhea-kegg.compound"
        )

        files_test = dict(
            chebi_compound_file = "compounds_test.tsv",
            chebi_chemical_data_file =  "chemical_data_test.tsv",
            #rhea_kegg_compound_file =  "rhea-kegg-test.compound"
        )

        Compound.create_compounds_from_files(input_db_dir, **files_test)
        Controller.save_all()
        self.assertEqual(Compound.get(Compound.source_accession == 'CHEBI:58321').name, 'L-allysine zwitterion')
        self.assertEqual(Compound.get(Compound.source_accession == 'CHEBI:59789').name, 'S-adenosyl-L-methionine zwitterion')
        
        
        