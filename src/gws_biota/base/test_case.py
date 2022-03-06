# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

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