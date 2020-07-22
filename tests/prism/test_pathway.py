import sys
import os
import unittest

from gws.settings import Settings
from biota.prism.pathway import Pathway, PathwayJSONViewModel

############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")


class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Pathway.drop_table()
        Pathway.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Pathway.drop_table()
        pass

    def test_db_object(self):
        print('test is ok')