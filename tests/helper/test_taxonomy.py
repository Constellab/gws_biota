import sys
import os
import unittest

from gws.settings import Settings
from biota.helper.taxonomy import Taxo
import re

####################################################################################
#
#                                  TEST TAXONOMY PARSER
#
####################################################################################

class TestModel(unittest.TestCase):

    def test_db_object(self):        
        settings = Settings.retrieve()
        path = settings.get_data("taxonomy_test_data_dir")
        
        files = dict(
            ncbi_nodes = "nodes_test.dmp",
            ncbi_names = "names_test.dmp",
            ncbi_division = "division.dmp",
            ncbi_citations = "citations.dmp"
        )
        #### Test taxonomy parser ####
        #dict_taxons = Taxo.get_all_taxonomy(path, **files)
        #self.assertEqual(dict_taxons['1'], {'tax_id': '1', 'ancestor': '1', 'rank': 'no rank', 'division': 'Unassigned', 'scientific_name': 'root'})
        #self.assertEqual(dict_taxons['10'], {'tax_id': '10', 'ancestor': '1706371', 'rank': 'genus', 'division': 'Bacteria', 'scientific_name': 'Cellvibrio'})
        #dict_taxons = Taxo.get_all_taxonomy(path **files)
        dict_ncbi_names = Taxo.get_ncbi_names(path, **files)
        start = 0
        stop = 0
        bulk_size = 10
        nodes_path = os.path.join(path, files['ncbi_nodes'])
        
        with open(nodes_path) as fh:
            size_file = len(fh.readlines())
        while True:
            if start >= size_file-1:
                break
            stop = min(start+bulk_size, size_file-1)
            print(start, stop)

            dict_taxons = Taxo.get_all_taxonomy(path, dict_ncbi_names, **files)
            
            if(dict_taxons == None):
                break

            print('-----------------------------------------------')   
            print(dict_taxons)
            print('-----------------------------------------------')
            start = stop+1