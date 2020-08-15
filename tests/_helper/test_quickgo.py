import sys
import os
import unittest

from biota._helper.quickgo import QuickGOAnnotation
import re


####################################################################################
#
#                                  TEST QiuckGo LOADER and PARSER
#
####################################################################################

class TestModel(unittest.TestCase):


    def test_db_object(self):
        list_annotations = QuickGOAnnotation.get_tsv_file_from_uniprot_id('A0A0J9X1MB')
        list_annotations = QuickGOAnnotation.get_tsv_file_from_uniprot_id('P38115')
        print(list_annotations)

