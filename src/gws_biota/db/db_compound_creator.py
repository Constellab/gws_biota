

import requests
from gws_core import (
    ConfigParams,
    ConfigSpecs,
    FileDownloader,
    InputSpec,
    InputSpecs,
    Logger,
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

from gws_biota import Compound
from gws_biota.compound.compound import CompoundAncestor
from gws_biota.compound.compound_service import CompoundService

from .db_service import DbService


@task_decorator("CompoundDBCreator", short_description="Download the online file ChEBI.obo (Chemical Entities of Biological Interest) and use it to load the “biota_compound” table from the BIOTA database.")
class CompoundDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})

    config_specs = ConfigSpecs({"compound_file": StrParam(
        default_value="https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        self.log_info_message("=" * 60)
        self.log_info_message("COMPOUND DATABASE CREATOR - STARTING")
        self.log_info_message("=" * 60)

        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Log current state
        self.log_info_message("Checking current database state...")
        try:
            compound_count_before = Compound.select().count()
            self.log_info_message(f"Current Compound records: {compound_count_before}")
        except:
            self.log_info_message("Current Compound records: Table doesn't exist or is empty")

        try:
            ancestor_count_before = CompoundAncestor.select().count()
            self.log_info_message(f"Current CompoundAncestor records: {ancestor_count_before}")
        except:
            self.log_info_message("Current CompoundAncestor records: Table doesn't exist or is empty")

        # Deleting the database...
        self.log_info_message("-" * 60)
        self.log_info_message("Deleting the CHEBI database...")
        DbService.drop_biota_tables([Compound, CompoundAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables dropped successfully")

        # ... to build it from 0
        self.log_info_message("Creating the CHEBI database...")
        DbService.create_biota_tables([Compound, CompoundAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables created successfully")

        # Verify tables are empty
        try:
            compound_count = Compound.select().count()
            ancestor_count = CompoundAncestor.select().count()
            self.log_info_message(f"Verification - Compound: {compound_count}, Ancestor: {ancestor_count}")
        except Exception as e:
            self.log_info_message(f"Could not verify: {e}")

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                Logger.info(f"{key}: OK - {url}")
                self.log_info_message(f"✓ {key}: URL validated")
            except requests.exceptions.RequestException as e:
                Logger.error(f"{key}: Error - {url}\n{e}")
                self.log_info_message(f"✗ {key}: URL validation failed")

        self.log_info_message("chebi.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create COMPOUND ------------- #
        # download file
        self.log_info_message("Downloading chebi.obo...")
        compound_file_path = file_downloader.download_file_if_missing(
            params["compound_file"], filename="chebi.obo")
        self.log_info_message("✓ chebi.obo downloaded")

        CompoundService.create_compound_db(destination_dir, compound_file_path, self.message_dispatcher)

        # Final verification
        try:
            final_compound_count = Compound.select().count()
            final_ancestor_count = CompoundAncestor.select().count()
            self.log_info_message(f"Final - Compound: {final_compound_count}, Ancestor: {final_ancestor_count}")
        except Exception as e:
            self.log_info_message(f"Could not get final counts: {e}")

        self.log_info_message("=" * 60)
        self.log_info_message("COMPOUND DATABASE CREATOR - COMPLETED")
        self.log_info_message("=" * 60)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        return {}
