import sys
import os
import unittest
import asyncio

from biota.db.compound import Compound
from biota.db.enzyme import Enzyme

class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #EnzymeStatistics.drop_table()
        #EnzymeStatisticsExtractor.drop_table()
        #EnzymeStatistics.create_table()
        #EnzymeStatisticsExtractor.create_table()
        pass

    @classmethod
    def tearDownClass(cls):
        #EnzymeStatistics.drop_table()
        #EnzymeStatisticsExtractor.drop_table()
        #Compound.drop_table()
        #Enzyme.drop_table()
        pass

    def test_process(self):
        return
        s = EnzymeStatisticsExtractor(title="stats")
        s.set_param('global_informations', True)
        s.set_param('organism', "Octopus vulgaris")
        
        def _on_end(*args, **kwargs):
            o = s.output['EnzymeStatistics']
            o.save()
            self.assertTrue( o.is_saved() )
            
            print(o.data)
        
        s.on_end(_on_end)
        e = s.create_experiment()
        
        asyncio.run( e.run() )

