import sys
import os
import unittest
import asyncio

from biota.db.enzyme_function import EnzymeFunctionStatistics, \
                                    StatisticsExtractor, \
                                    EnzymeFunctionStatisticsJSONViewModel

class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeFunctionStatistics.drop_table()
        StatisticsExtractor.drop_table()
        EnzymeFunctionStatistics.create_table()
        StatisticsExtractor.create_table()
        pass

    @classmethod
    def tearDownClass(cls):
        EnzymeFunctionStatistics.drop_table()
        StatisticsExtractor.drop_table()
        pass

    def test_process(self):
        asyncio.run( self._process() )

    async def _process(self):
        s = StatisticsExtractor()
        s.set_param('global_informations', True)
        s.set_param('organism', "Octopus vulgaris")
        await s.run()

        s.output['EnzymeFunctionStatistics'].save()
  
        vmodel = EnzymeFunctionStatisticsJSONViewModel(s.output['EnzymeFunctionStatistics'])
        view = vmodel.render()
        print(len(view))
        print(view)
        #for i in range(0, 10):
            #print(view[i])
        #self.assertEqual(view[10], 7)