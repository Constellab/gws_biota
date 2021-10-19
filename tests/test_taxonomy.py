from gws_core import Settings, BaseTestCase
from gws_biota import Taxonomy
from gws_biota.taxonomy.taxonomy_service import TaxonomyService

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestTaxonomy(BaseTestCase):

    def test_db_object(self):
        self.print("Taxonomy")
        params = dict(
            biodata_dir = testdata_path,
            ncbi_node_file = "nodes_test.dmp",
            ncbi_name_file = "names_test.dmp",
            ncbi_division_file = "division.dmp",
            ncbi_citation_file = "citations.dmp"
        )
        TaxonomyService.create_taxonomy_db(**params)
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 72).data, {'tax_id': '72', 'rank': 'species', 'division': 'Bacteria'})
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 1).data, {'tax_id': '1', 'name': 'root', 'rank': 'no rank', 'division': 'Unassigned'})
        
        #Q = Taxonomy.select()
        #for t in Q:
        #    print(t.title)
        
        Q = Taxonomy.search("methylotrophus")
        print(len(Q))
        self.assertEqual(Q[0].name, "Methylophilus methylotrophus")
        