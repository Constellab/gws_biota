import pickle

from gws_biota import BaseTestCaseUsingFullBiotaDB, Unicell
from gws_biota.unicell.unicell_service import UnicellService
from gws_core import BaseTestCase, Settings

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")


class TestUnicell(BaseTestCaseUsingFullBiotaDB):

    def test_db_object(self):
        self.print("Unicell")
        params = dict()
        uc = UnicellService.create_unicell_db()

        # Q = Unicell.select()
        # print(len(Q))
        # uc = Q[0]

        # print(uc.get_compound_id_list())
        # print(uc.get_reaction_id_list())

        # for _id in uc.get_compound_id_list():
        #     if "CHEBI:15361" == _id:
        #         print(id)

        #     if "CHEBI:15361" == _id:
        #         print(id)

        # uc.are_connected()
