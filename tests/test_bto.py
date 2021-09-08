from gws_core import Settings, GTest, BaseTestCase
from gws_biota import BTO
from gws_biota.bto.bto_service import BTOService

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")
 
class TestBTO(BaseTestCase):

    def test_db_object(self):
        GTest.print("BTO")
        params = dict(
            biodata_dir = testdata_path,
            bto_file = "bto_test.json",
        )
        BTOService.create_bto_db(**params)
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').get_name(), 'tissues, cell types and enzyme sources')        
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000002').get_name(), 'culture condition:1,4-dichlorobenzene-grown cell')