import sys
import os
import unittest


from peewee import CharField
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from manage import settings
from peewee import CharField, chunked
from brenda.brenda import Brenda
from gena.enzyme import Enzyme

import logging
from collections import OrderedDict
from brendapy import BrendaParser, BrendaProtein
from brendapy.taxonomy import Taxonomy

from brendapy import utils
from brendapy.taxonomy import Taxonomy
from brendapy.tissues import BTO
from brendapy.substances import CHEBI


############################################################################################
#
#                                        TestEnzymes
#                                         
############################################################################################

input_db_dir = settings.get_data("gena_db_path")

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Enzyme.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Enzyme.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            brenda_file = "brenda_download.txt"
        )

        files_test = dict(
            brenda_file = "brenda_test.txt"
        )

        #brenda = Brenda(os.path.join(input_db_dir, file))
        #list_ = brenda.parse_all_protein_to_dict()
        Enzyme.create_enzymes_from_dict(input_db_dir, **files_test)

        Controller.save_all()
