from gws_biota import Compound, Pathway
from gws_biota.pathway.pathway_service import PathwayService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestPatwhays(BaseTestCase):

    def test_db_object(self):
        self.print("Pathway")
        cid = ["10033", "10036", "10049", "10055", "10093", "16027", "16284", "17111"]
        for _id in cid:
            c = Compound(chebi_id="CHEBI:"+_id)
            c.save()

        params = dict(
            biodata_dir = testdata_path,
            reactome_pathways_file =  'reactome_pathways.txt',
            reactome_pathway_relations_file = 'reactome_pathway_relations.txt',
            reactome_chebi_pathways_file = 'reactome_chebi.txt',
        )
        PathwayService.create_pathway_db(**params)

        p = Pathway.get(Pathway.reactome_pathway_id == "R-BTA-1296025")
        self.assertEqual( p.get_name(), "ATP sensitive Potassium channels" )

        p = Pathway.get(Pathway.reactome_pathway_id == "R-BTA-73843")
        self.assertEqual( p.get_name(), "5-Phosphoribose 1-diphosphate biosynthesis" )
        self.assertEqual( len(p.ancestors), 1 )
        self.assertEqual( p.ancestors[0].get_name(), "Pentose phosphate pathway" )