import os
from unittest import TestCase

from gws_biota.db.biota_db_downloader import BiotaDbDownloader
from gws_core import Settings, TaskRunner


# test_biota_db_downloader.py
class TestBiotaDbDownloader(TestCase):
    """Unit tests for the BiotaDbDownloader task."""

    def test_download_biota_db(self):
        """Test real download of Biota database from settings."""
        self.skipTest("Requires Docker infrastructure and network access")
        runner = TaskRunner(
            task_type=BiotaDbDownloader,
            params={
                "force_redownload": False,
            },
        )

        runner.run()
