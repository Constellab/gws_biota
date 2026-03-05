import tempfile

from gws_biota.apps.biota_app.generate_biota_app import GenerateBiotaApp
from gws_core import File
from gws_core.test.app_tester import AppTester
from gws_core.test.base_test_case import BaseTestCase


# test_apps
class TestApps(BaseTestCase):

    def _create_empty_config_file(self) -> File:
        """Create a File resource containing an empty JSON object."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{}")
            tmp_path = tmp.name
        return File(tmp_path)

    def test_biota_app(self):
        config_file = self._create_empty_config_file()

        AppTester.test_app_from_task(
            test_case=self,
            generate_task_type=GenerateBiotaApp,
            app_output_name="reflex_app",
            input_resources={"app_config": config_file},
            config_values={
                "chat_app_name": "test",
            },
        )
