import sys
import os
import unittest
import asyncio

from biota.db.enzyme_function import EnzymeFunctionStatistics, EnzymeFunctionStatisticsProcess, EnzymeFunctionStatisticsJSONViewModel

############################################################################################
#
#                                        TestsStats
#                                         
############################################################################################


class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeFunctionStatistics.drop_table()
        EnzymeFunctionStatisticsProcess.drop_table()
        pass

    @classmethod
    def tearDownClass(cls):
        EnzymeFunctionStatistics.drop_table()
        EnzymeFunctionStatisticsProcess.drop_table()
        pass

    def test_process(self):
        asyncio.run( self._process() )

    async def _process(self):
        stats = EnzymeFunctionStatistics()
        s1 = EnzymeFunctionStatisticsProcess()
        s1.input['EnzymeFunctionStatistics'] = stats
        params = {'global_informations': True, 'organism': "Octopus vulgaris"}
        await s1.run(params)
        s1.output['EnzymeFunctionStatistics'].save()
        #self.assertEqual(s1.output['EnzymeFunctionStatistics'].data['enzyme_function_count'], 7)
        #self.assertEqual(s1.output['EnzymeFunctionStatistics'].data['number_of_references'], 7)
        #self.assertEqual(s1.output['EnzymeFunctionStatistics'].data['number_of_organisms'], 7)
        
        enzymestat1_view_model = EnzymeFunctionStatisticsJSONViewModel(s1.output['EnzymeFunctionStatistics'])
        view = enzymestat1_view_model.render()
        print(len(view))
        print(view)
        #for i in range(0, 10):
            #print(view[i])
        #self.assertEqual(view[10], 7)