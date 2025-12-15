from unittest import TestCase

from gws_biota.db.biota_db_downloader import BiotaDbDownloader
from gws_core import TaskRunner


# test_biota_db_downloader.py
class TestBiotaDbDownloader(TestCase):
    """Unit tests for the BiotaDbDownloader task."""

    def test_download_biota_db(self):
        """Test real download of Biota database from settings."""
        # Run the task without providing db_url (will use settings)
        runner = TaskRunner(
            task_type=BiotaDbDownloader,
            params={
                "force_redownload": False,
            },
        )

        # Execute the task
        outputs = runner.run()

        # Verify the task completed successfully
        self.assertIsNotNone(outputs)
