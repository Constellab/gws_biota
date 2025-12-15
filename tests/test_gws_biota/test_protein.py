from gws_biota.protein.protein_service import ProteinService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestGO(BaseTestCase):
    def test_db_object(self):
        self.print("Protein")
        params = dict(
            biodata_dir=testdata_path,
            protein_file="uniprot_sprot.fasta",
        )
        ProteinService.create_protein_db(**params)
