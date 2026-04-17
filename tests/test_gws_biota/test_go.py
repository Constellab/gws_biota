from gws_biota import GO
from gws_biota.go.go_service import GOService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestGO(BaseTestCase):
    def test_db_object(self):
        GOService.create_go_db(path=testdata_path, go_file="go_test.obo")
        self.assertEqual(GO.get(GO.go_id == "GO:0000001").get_name(), "mitochondrion inheritance")
        self.assertEqual(
            GO.get(GO.go_id == "GO:0000006").get_name(),
            "high-affinity zinc transmembrane transporter activity",
        )
