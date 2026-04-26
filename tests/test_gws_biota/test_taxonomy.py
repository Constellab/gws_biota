from gws_biota import Taxonomy
from gws_biota.taxonomy.taxonomy_service import TaxonomyService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestTaxonomy(BaseTestCase):
    def test_db_object(self):
        self.print("Taxonomy")
        TaxonomyService.create_taxonomy_db(path=testdata_path, taxdump_files=testdata_path)
        self.assertEqual(
            Taxonomy.get(Taxonomy.tax_id == 72).data,
            {"tax_id": "72", "rank": "species", "division": "Bacteria"},
        )
        self.assertEqual(
            Taxonomy.get(Taxonomy.tax_id == 1).data,
            {"tax_id": "1", "name": "root", "rank": "no rank", "division": "Unassigned"},
        )

        # Q = Taxonomy.select()
        # for t in Q:
        #    print(t.title)

        Q = Taxonomy.search("methylotrophus")
        print(len(Q))
        self.assertEqual(Q[0].name, "Methylophilus methylotrophus")
