import unittest

from gws_core import BaseTestCase

from ..db.biota_db_manager import BiotaDbManager


class BaseTestCaseUsingFullBiotaDB(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            BiotaDbManager().init(mode="dev")
        except Exception:
            raise unittest.SkipTest("Dev Biota database is not available in this environment")

    @classmethod
    def tearDownClass(cls):
        BiotaDbManager().init(mode="test")
        super().tearDownClass()
