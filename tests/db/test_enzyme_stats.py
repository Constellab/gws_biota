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
        pass