import sys
import os
import unittest


from peewee import CharField
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gena.compound import Compound, CompoundHTMLViewModel, CompoundJSONViewModel
from chebi.chebi import Chebi
from rhea.rhea import Rhea
from manage import settings
from peewee import CharField, chunked


############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################
#path = os.path.realpath('./databases_input') #Set the path where we can find input data
input_db_dir = settings.get_data("gena_db_path")

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
            rhea_kegg_compound_file =  "rhea-kegg.compound"
        )

        files_test = dict(
            chebi_compound_file = "compounds_test.tsv",
            chebi_chemical_data_file =  "chemical_data_test.tsv",
            rhea_kegg_compound_file =  "rhea-kegg-test.compound"
        )

        #Compound.create_compounds_from_files(input_db_dir, **files_test)
        #Controller.save_all()

        ## Atomics tests for compounds' functions ##
        
        list_comp = Chebi.parse_csv_from_file(input_db_dir, files['chebi_compound_file'])
        Compound.create_compounds(list_comp)
        #self.assertEqual(len(list_comp), 299)
        self.assertEqual(list_comp[0]['chebi_accession'], 'CHEBI:9437')
        self.assertEqual(list_comp[8]['name'], 'salicyluric acid')

        Controller.save_all()
        """
        list_chemical = Chebi.parse_csv_from_file(input_db_dir, files['chebi_chemical_data_file'])
        Compound.set_chemicals(list_chemical)
        #self.assertEqual(list_chemical[0],{'id': '1', 'compound_id': '18357', 'source': 'KEGG COMPOUND', 'type': 'FORMULA', 'chemical_data': 'C8H11NO3'})
        
        list_compound_reactions = Rhea.parse_compound_from_file(input_db_dir, files['rhea_kegg_compound_file'])
        Compound.set_reactions_from_list(list_compound_reactions)
        self.assertEqual(list_compound_reactions[0]['reaction'],['32539', '32540', '32541', '32542'])
        print(list_comp[0]['chebi_accession'])
        print(type(list_comp[0]['chebi_accession']))
        Controller.save_all()
        """
        
        
        
        