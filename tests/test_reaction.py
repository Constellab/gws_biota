import unittest
import copy
from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Resource
from gws.prism.controller import Controller



import sys
import os
import unittest

import asyncio

from peewee import CharField, ForeignKeyField
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from gws.prism.controller import Controller
from compound import Reaction, ReactionHTMLViewModel, ReactionJSONViewModel

class TestCompound(unittest.TestCase):
    Reaction.drop_table()
    Reaction.create_table()
    
    def test_db_object(self):
        reaction_test = Reaction()
        reaction_test.data["ID"] = 9347

        html_vm = ReactiondHTMLViewModel(reaction_test)
        json_vm = ReactiondJSONViewModel(reaction_test)

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
        print(html_vm.data)
