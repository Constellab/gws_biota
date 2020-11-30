import sys
import os
import unittest
import asyncio

from biota.db.enzyme import EnzymeStatistics, EnzymeStatisticsExtractor
from biota.db.compound import Compound
from biota.db.enzyme import Enzyme

class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeStatistics.drop_table()
        EnzymeStatisticsExtractor.drop_table()
        EnzymeStatistics.create_table()
        EnzymeStatisticsExtractor.create_table()
        pass

    @classmethod
    def tearDownClass(cls):
        EnzymeStatistics.drop_table()
        EnzymeStatisticsExtractor.drop_table()
        Compound.drop_table()
        Enzyme.drop_table()
        pass

    async def _process(self):
        s = EnzymeStatisticsExtractor()
        s.set_param('global_informations', True)
        s.set_param('organism', "Octopus vulgaris")

        e = s.create_experiment()
        await e.run()

        s.output['EnzymeStatistics'].save()
        self.assertTrue( s.is_saved() )
