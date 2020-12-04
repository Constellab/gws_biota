import sys
import os
import unittest
import asyncio

from gws.controller import Controller
from gws.settings import Settings
from biota.db.enzyme import EnzymeStatistics, EnzymeStatisticsExtractor
from biota.db.bto import BTO


settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestEnzymeStatistics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        EnzymeStatistics.drop_table()
        EnzymeStatistics.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        def _on_end(*args, **kwargs):
            stats = EnzymeStatistics.get_by_id(1)
            print(f"Count = {EnzymeStatistics.select().count()}")
            print(stats.data)

        proc = EnzymeStatisticsExtractor()
        proc.on_end(_on_end)
        e = proc.create_experiment()
        asyncio.run( e.run() )