
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
        path = settings.get_data("biota:taxonomy_testdata_dir")
        
        files = dict(
            ncbi_nodes = "nodes_test.dmp",
            ncbi_names = "names_test.dmp",
            ncbi_division = "division.dmp",
            ncbi_citations = "citations.dmp"
        )


        dict_ncbi_names = NCBITaxonomy.get_ncbi_names(path, **files)
        dict_taxons = NCBITaxonomy.get_all_taxonomy(path, dict_ncbi_names, **files)
        
        print('')   
        print(dict_taxons)
        print('')
