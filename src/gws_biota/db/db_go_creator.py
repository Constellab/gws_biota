

import requests
from gws_core import (
    ConfigParams,
    ConfigSpecs,
    FileDownloader,
    InputSpec,
    InputSpecs,
    OutputSpec,
    OutputSpecs,
    Settings,
    StrParam,
    Task,
    TaskInputs,
    TaskOutputs,
    Text,
    task_decorator,
)

from gws_biota import GO
from gws_biota.go.go_service import GOService

from .db_service import DbService


@task_decorator("GoDBCreator", short_description="Download the online file GO (Gene Ontology) and use it to load the “biota_go” table from the BIOTA database.")
class GoDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({
        "go_file": StrParam(default_value="https://current.geneontology.org/ontology/go.obo")
    })

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Deleting the database...
        self.log_info_message("Deleting the GO database...")
        DbService.drop_biota_tables([GO])

        # ... to build it from 0
        self.log_info_message("Creating the GO database...")
        DbService.create_biota_tables([GO])

        # Checks that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("go.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create GO ------------- #
        # download file
        go_file = file_downloader.download_file_if_missing(
            params["go_file"], filename="go.obo")

        GOService.create_go_db(destination_dir, go_file)
