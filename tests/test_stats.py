import sys
import os
import unittest
import asyncio


from peewee import CharField, chunked
from gws.prism.model import Model, Process, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from gws.prism.app import App
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate

from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from manage import settings
from biota.enzyme import Enzyme, EnzymeStatistics, process_statistics, EnzymeStatisticsJSONViewModel
import re

############################################################################################
#
#                                        TestsStats
#                                         
############################################################################################


class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeStatistics.drop_table()
        process_statistics.drop_table()
        pass

    @classmethod
    def tearDownClass(cls):
        EnzymeStatistics.drop_table()
        process_statistics.drop_table()
        pass

    def test_process(self):
        asyncio.run( self._process() )

    async def _process(self):
        stats = EnzymeStatistics()
        s1 = process_statistics()
        s1.input['EnzymeStatistics'] = stats
        params = {'global_informations': True, 'organism': "Octopus vulgaris"}
        await s1.run(params)
        s1.output['EnzymeStatistics'].save()
        self.assertEqual(s1.output['EnzymeStatistics'].data['total_number_of_enzyme'], 7)
        self.assertEqual(s1.output['EnzymeStatistics'].data['number_of_references'], 7)
        self.assertEqual(s1.output['EnzymeStatistics'].data['number_of_organisms'], 7)
        
        enzymestat1_view_model = EnzymeStatisticsJSONViewModel(s1.output['EnzymeStatistics'])
        view = enzymestat1_view_model.render()
        print(len(view))
        print(view)
        #for i in range(0, 10):
            #print(view[i])
        #self.assertEqual(view[10], 7)