from gws_biota import ECO
from gws_biota.eco.eco_service import ECOService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota:testdata_dir")


class TestECO(BaseTestCase):

    def test_db_object(self):
        self.print("ECO")
        params = dict(
            biodata_dir = testdata_path,
            eco_file = "eco_test.obo",
        )

        ECOService.create_eco_db(**params)
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').get_name(), "inference from background scientific knowledge")
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000002').get_name(), "direct assay evidence")

        Q = ECO.search('ECO0000002')
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].get_name(), 'direct assay evidence')