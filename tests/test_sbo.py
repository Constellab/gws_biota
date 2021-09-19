from gws_core import Settings, BaseTestCase
from gws_biota import SBO
from gws_biota.sbo.sbo_service import SBOService

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestSBO(BaseTestCase):

    def test_db_object(self):
        self.print("SBO")
        params = dict(
            biodata_dir = testdata_path,
            sbo_file = "sbo_test.obo",
        )
    
        SBOService.create_sbo_db(**params)
        self.assertEqual(SBO.get(SBO.sbo_id == 'SBO:0000000').get_name(), 'systems biology representation')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000005").get_name(), 'obsolete mathematical expression')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000004").get_name(), 'modelling framework')

