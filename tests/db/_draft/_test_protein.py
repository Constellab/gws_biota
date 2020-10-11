import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.enzyme import Enzyme

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestEnzyme(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Enzyme.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        return
        files_test = dict(
            brenda_file = "brenda_test.txt"
        )

        Enzyme.create_protein_db(testdata_path, **files_test)


# class TestGetUniprotID(unittest.TestCase):
#     import urllib.parse
#     import urllib.request

#     url = 'https://www.uniprot.org/uploadlists/'

#     params = {
#     'from': 'EC',
#     'to': 'UNIPROT_ID',
#     'format': 'tab',
#     'query': 'EC1.1.1.117'
#     }

#     data = urllib.parse.urlencode(params)
#     data = data.encode('utf-8')
#     req = urllib.request.Request(url, data)
    
#     with urllib.request.urlopen(req) as f:
#         response = f.read()

#     print(response.decode('utf-8'))