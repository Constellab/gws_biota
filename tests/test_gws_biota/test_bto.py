from gws_biota import BTO
from gws_biota.bto.bto_service import BTOService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestBTO(BaseTestCase):
    def test_db_object(self):
        self.print("BTO")
        params = dict(
            biodata_dir=testdata_path,
            bto_file="bto_test.obo",
        )
        BTOService.create_bto_db(**params)
        self.assertEqual(
            BTO.get(BTO.bto_id == "BTO:0000000").get_name(),
            "tissues, cell types and enzyme sources",
        )
        self.assertEqual(
            BTO.get(BTO.bto_id == "BTO:0000002").get_name(),
            "culture condition:1,4-dichlorobenzene-grown cell",
        )

        b = BTO.get(BTO.bto_id == "BTO:0000002")
        print(b.ft_names)

        Q = BTO.search("BTO0000002")
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].get_name(), "culture condition:1,4-dichlorobenzene-grown cell")
