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
from hello.compound import Compound, CompoundHTMLViewModel, CompoundJSONViewModel
from peewee import CharField

############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Compound.create_table()
        Compound.create(name = 'Test0', data = {'ID':9347})
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):

        compound_test = Compound.get(Compound.name == 'Test0')
        compound_test.save()
        compound_test1 = Compound.create(name = 'Test1', data = {'ID': 9231})
        compound_test1.save()
        self.assertEqual(compound_test.data['ID'], 9347)
        
        html_vm = CompoundHTMLViewModel(compound_test)
        json_vm = CompoundJSONViewModel(compound_test)

        html_vm.save()
        params = {'Color':'red'}
        htmltext = html_vm.render(params)
        filetext = compound_test1.OpenFile('test')

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
        
        print(htmltext)
        print(filetext)