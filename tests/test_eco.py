from gws_core import Settings, GTest, BaseTestCase
from gws_biota import ECO
from gws_biota.eco.eco_service import ECOService

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")


class TestECO(BaseTestCase):

    def test_db_object(self):
        GTest.print("ECO")
        params = dict(
            biodata_dir = testdata_path,
            eco_file = "eco_test.obo",
        )

        ECOService.create_eco_db(**params)
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').get_name(), "inference from background scientific knowledge")
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000002').get_name(), "direct assay evidence")
