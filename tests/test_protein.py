from gws_core import Settings, GTest, BaseTestCase
from gws_biota.protein.protein_service import ProteinService

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestGO(BaseTestCase):

    def test_db_object(self):
        GTest.print("Protein")
        params = dict(
            biodata_dir = testdata_path,
            protein_file = "uniprot_sprot.fasta",
        )
        ProteinService.create_protein_db(**params)  

                