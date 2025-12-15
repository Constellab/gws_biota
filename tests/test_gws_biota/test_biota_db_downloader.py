import os
from unittest import TestCase

from gws_biota.db.biota_db_downloader import BiotaDbDownloader
from gws_core import Settings, TaskRunner


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
        runner.run()

        destination_folder = os.path.join(
            Settings.get_instance().get_brick_data_dir("gws_biota"),
            BiotaDbDownloader.BRICK_DATA_FOLDER,
        )

        # Verify that the database folder was created and it contains a 'mariadb' subfolder
        mariadb_folder = os.path.join(destination_folder, "mariadb")
        self.assertTrue(
            os.path.exists(destination_folder), "Destination folder was not created."
        )
        self.assertTrue(
            os.path.exists(mariadb_folder),
            "'mariadb' folder was not created inside destination folder.",
        )
