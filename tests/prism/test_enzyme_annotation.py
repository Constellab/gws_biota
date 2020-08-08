import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.db.enzyme_annotation import EnzymeAnnotation

settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")

class TestEnzymeAnnotation(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        EnzymeAnnotation.drop_table()
        EnzymeAnnotation.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass
        

    def test_db_object(self):
        pass
        