import gzip
import os
import shutil

from gws_biota.protein.protein_service import ProteinService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestGO(BaseTestCase):
    def test_db_object(self):
        self.print("Protein")
        gz_path = os.path.join(testdata_path, "uniprot_sprot.fasta.gz")
        if not os.path.exists(gz_path):
            with open(os.path.join(testdata_path, "uniprot_sprot.fasta"), "rb") as f_in:
                with gzip.open(gz_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        ProteinService.create_protein_db(path=testdata_path, protein_file=gz_path)
