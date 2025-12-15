import os

from gws_biota import Compound
from gws_biota.compound.compound_service import CompoundService
from gws_core import BaseTestCase, Settings

############################################################################################
#
#                                        TestChebiOntology
#
############################################################################################
settings = Settings.get_instance()
testdata_path = os.path.join(settings.get_variable("gws_biota", "testdata_dir"), "../_helper/data/")


class TestCompound(BaseTestCase):
    def test_db_object(self):
        self.print("Compound")
        params = dict(
            biodata_dir=testdata_path,
            chebi_file="chebi_test.obo",
        )
        CompoundService.create_compound_db(**params)
        self.assertEqual(
            Compound.get(Compound.chebi_id == "CHEBI:24431").get_name(), "chemical entity"
        )
        self.assertEqual(Compound.get(Compound.chebi_id == "CHEBI:17051").get_name(), "fluoride")

        comp = Compound.get(Compound.chebi_id == "CHEBI:49499")
        self.assertEqual(comp.get_name(), "beryllium difluoride")

        self.assertEqual(len(comp.ancestors), 1)
        self.assertEqual(comp.ancestors[0].get_name(), "fluoride salt")

        comp = Compound.get(Compound.chebi_id == "CHEBI:17051")
        self.assertEqual(comp.alt_chebi_ids, ["CHEBI:14271", "CHEBI:49593", "CHEBI:5113"])
        print(comp.alt_chebi_ids)

        Q = Compound.search("CHEBI17051")
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].name, "fluoride")

        Q = Compound.search("CHEBI17051 CHEBI14271")
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].name, "fluoride")

        Q = Compound.search("CHEBI49593")
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].name, "fluoride")

        Q = Compound.search("CHEBI:")
        self.assertEqual(len(Q), 0)

        Q = Compound.search_by_chebi_ids(["49593", "CHEBI24431"])
        self.assertEqual(len(Q), 2)
