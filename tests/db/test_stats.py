import sys
import os
import unittest
import asyncio

from biota.db.enzyme import EnzymeStatistics, StatisticsExtractor
from biota.db.compound import Compound
from biota.db.enzyme import Enzyme

class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeStatistics.drop_table()
        StatisticsExtractor.drop_table()
        EnzymeStatistics.create_table()
        StatisticsExtractor.create_table()
        pass

    @classmethod
    def tearDownClass(cls):
        EnzymeStatistics.drop_table()
        StatisticsExtractor.drop_table()
        Compound.drop_table()
        Enzyme.drop_table()
        pass

    def test_process(self):
        asyncio.run( self._process() )

    async def _process(self):
        s = StatisticsExtractor()
        s.set_param('global_informations', True)
        s.set_param('organism', "Octopus vulgaris")
        await s.run()

        s.output['EnzymeStatistics'].save()
        self.assertTrue( s.is_saved() )
