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
from chebi.csv_parser import parse_csv_from_file, parse_csv_from_list
from rhea.compound_parser import parse_compound_from_file
from manage import settings
from peewee import CharField, chunked


############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################
#path = os.path.realpath('./databases_input') #Set the path where we can find input data
path = settings.get_data("gena_db_path")

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
        list_comp = parse_csv_from_file(path, 'compounds.tsv')
        Compound.create_compounds(self, list_comp)
        Controller.save_all()

        list_chemical = parse_csv_from_file(path, 'chemical_data.tsv')
        Compound.get_chemicals(self, list_chemical)
        
        #structures = parse_csv_from_file(path, 'structures.csv')
        #comp = Compound.get(Compound.source_accession == 'CHEBI:18357')
        #print(comp.name)
        #comp.save()
        #Compound.save(self)
        list_compound_reactions = parse_compound_from_file(path, 'rhea-kegg.compound')
        Compound.get_reactions(self, list_compound_reactions)
        Controller.save_all()
        

        async def app(scope, receive, send):
            assert scope['type'] == 'http'
            request = Request(scope, receive)
            vm = await Controller.action(request)
            html = vm.render()
            response = HTMLResponse(html)
            await response(scope, receive, send)

        Controller.is_query_params = True
        client = TestClient(app)
        
        """
        # Test update_view => html
        params = ""
        response = client.get(Controller.build_url(
            action = 'view', 
            uri_name = html_vm.uri_name,
            uri_id = html_vm.uri_id,
            params = params
        ))

        self.assertEqual(response.status_code, 200)
        print(response.content)


        response = client.get(Controller.build_url(
            action = 'view', 
            uri_name = json_vm.uri_name,
            uri_id = json_vm.uri_id,
            params = params
        ))

        self.assertEqual(response.status_code, 200)
        print(response.content)
        """
        #for i in range(0,10):
            #print(list_chemical[i])
        