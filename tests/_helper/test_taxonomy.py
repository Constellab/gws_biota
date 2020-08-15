
import unittest
from gws.settings import Settings
from biota._helper.ncbi import Taxonomy as NCBITaxonomy

####################################################################################
#
#                                  TEST TAXONOMY PARSER
#
####################################################################################

class TestModel(unittest.TestCase):

    def test_db_object(self):        
        settings = Settings.retrieve()
        path = settings.get_dir("biota:taxonomy_testdata_dir")
        
        files = dict(
            ncbi_node_file = "nodes_test.dmp",
            ncbi_name_file = "names_test.dmp",
            ncbi_division_file = "division.dmp",
            ncbi_citation_file = "citations.dmp"
        )

        dict_ncbi_names = NCBITaxonomy.get_ncbi_names(path, **files)
        dict_taxons = NCBITaxonomy.get_all_taxonomy(path, dict_ncbi_names, **files)
        
        self.assertEqual(dict_taxons['72'], {'tax_id': '72', 'ancestor': '71', 'rank': 'species', 'division': 'Bacteria'})
        self.assertEqual(dict_taxons['1'], {'tax_id': '1', 'name': 'root', 'ancestor': '1', 'rank': 'no rank', 'division': 'Unassigned'})