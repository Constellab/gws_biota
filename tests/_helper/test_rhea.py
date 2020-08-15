import sys
import os
import unittest

from gws.settings import Settings
from gws.prism.controller import Controller

from biota._helper.rhea import Rhea
from pronto import Ontology
import re

class TestModel(unittest.TestCase):

    def test_db_object(self):
        settings = Settings.retrieve()
        path_test = settings.get_dir("biota:rhea_testdata_dir")

        #### Test reaction parser ####
        list_reactions = Rhea.parse_reaction_from_file(path_test, 'rhea-kegg_test.reaction')
        self.assertEqual(len(list_reactions), 12)
        self.assertEqual(list_reactions[0]['entry'], 'RHEA:10022')
        self.assertEqual(list_reactions[1]['substrates'], ["CHEBI:15377","CHEBI:57951","CHEBI:58349"])

        #### Test compound parser ####
        list_compound = Rhea.parse_compound_from_file(path_test, 'rhea-kegg-test.compound')
        self.assertEqual(len(list_compound), 25)
        self.assertEqual(list_compound[0]['entry'], 'CHEBI:7')
        self.assertEqual(list_compound[1]['entry'], 'CHEBI:20')
        list_directions = Rhea.parse_csv_from_file(path_test, 'rhea-directions-test.tsv')

        cols = Rhea.get_columns_from_lines(list_directions)
        self.assertEqual(cols['UN'][0:5], ['10000', '10004', '10008', '10012', '10016'])
        self.assertEqual(cols['LR'][0:5], ['10001', '10005', '10009', '10013', '10017'])
        self.assertEqual(cols['RL'][0:5], ['10002', '10006', '10010', '10014', '10018'])
        self.assertEqual(cols['BI'][0:5], ['10003', '10007', '10011', '10015', '10019'])

        #### Test .csv/.tsv parser ####
        