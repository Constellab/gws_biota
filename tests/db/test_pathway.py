import sys
import os
import unittest

from gws.settings import Settings
from biota.db.pathway import Pathway

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")


class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Pathway.drop_table()
        Pathway.create_table()
   
    @classmethod
    def tearDownClass(cls):
        Pathway.drop_table()
        pass

    def test_db_object(self):
        pass