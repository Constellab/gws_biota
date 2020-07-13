import sys
import os
import unittest
import asyncio

from biota.enzyme import EnzymeStatistics, EnzymeStatisticsProcess, EnzymeStatisticsJSONViewModel

############################################################################################
#
#                                        TestsStats
#                                         
############################################################################################


class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeStatistics.drop_table()
        EnzymeStatisticsProcess.drop_table()
        pass

    @classmethod
    def tearDownClass(cls):
        EnzymeStatistics.drop_table()
        EnzymeStatisticsProcess.drop_table()
        pass

    def test_process(self):
        asyncio.run( self._process() )

    async def _process(self):
        stats = EnzymeStatistics()
        s1 = EnzymeStatisticsProcess()
        s1.input['EnzymeStatistics'] = stats
        params = {'global_informations': True, 'organism': "Octopus vulgaris"}
        await s1.run(params)
        s1.output['EnzymeStatistics'].save()
        #self.assertEqual(s1.output['EnzymeStatistics'].data['total_number_of_enzyme'], 7)
        #self.assertEqual(s1.output['EnzymeStatistics'].data['number_of_references'], 7)
        #self.assertEqual(s1.output['EnzymeStatistics'].data['number_of_organisms'], 7)
        
        enzymestat1_view_model = EnzymeStatisticsJSONViewModel(s1.output['EnzymeStatistics'])
        view = enzymestat1_view_model.render()
        print(len(view))
        print(view)
        #for i in range(0, 10):
            #print(view[i])
        #self.assertEqual(view[10], 7)