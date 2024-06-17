

from gws_core import BaseTestCase
from ..db.db_manager import DbManager as BiotaDbManager

class BaseTestCaseUsingFullBiotaDB(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BiotaDbManager.init(mode="dev")

    @classmethod
    def tearDownClass(cls):
        BiotaDbManager.init(mode="test")
        super().tearDownClass()