

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
    Text,
    task_decorator,
)

from gws_biota import BTO
from gws_biota.bto.bto import BTOAncestor
from gws_biota.bto.bto_service import BTOService

from .db_service import DbService


@task_decorator("BtoDBCreator", short_description="Download the online file bto.owl (The BRENDA Tissue Ontology) and use it to load the “biota_bto” table from the BIOTA database.")
class BtoDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"bto_file": StrParam(
        default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs):
        self.log_info_message("=" * 60)
        self.log_info_message("BTO DATABASE CREATOR - STARTING")
        self.log_info_message("=" * 60)

        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Log current state
        self.log_info_message("Checking current database state...")
        try:
            bto_count_before = BTO.select().count()
            self.log_info_message(f"Current BTO records: {bto_count_before}")
        except:
            self.log_info_message("Current BTO records: Table doesn't exist or is empty")

        try:
            ancestor_count_before = BTOAncestor.select().count()
            self.log_info_message(f"Current BTOAncestor records: {ancestor_count_before}")
        except:
            self.log_info_message("Current BTOAncestor records: Table doesn't exist or is empty")

        # Deleting the database...
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 1: Dropping existing tables")
        self.log_info_message("-" * 60)
        self.log_info_message("Deleting the BTO database...")
        DbService.drop_biota_tables([BTO, BTOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables dropped successfully")

        # ... to build it from 0
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 2: Creating new tables")
        self.log_info_message("-" * 60)
        self.log_info_message("Creating the BTO database...")
        DbService.create_biota_tables([BTO, BTOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables created successfully")

        # Verify tables are empty
        self.log_info_message("Verifying tables are empty...")
        try:
            bto_count = BTO.select().count()
            ancestor_count = BTOAncestor.select().count()
            self.log_info_message(f"  BTO: {bto_count} records")
            self.log_info_message(f"  BTOAncestor: {ancestor_count} records")

            if bto_count > 0 or ancestor_count > 0:
                self.log_info_message("⚠ WARNING: Tables not empty after creation!")
        except Exception as e:
            self.log_info_message(f"Could not verify: {e}")

        # Check that the url exists and works
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 3: Validating download URL")
        self.log_info_message("-" * 60)
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                Logger.info(f"{key}: OK - {url}")
                self.log_info_message(f"✓ {key}: URL validated")
            except requests.exceptions.RequestException as e:
                Logger.error(f"{key}: Error - {url}\n{e}")
                self.log_info_message(f"✗ {key}: URL validation failed")

        self.log_info_message("bto.owl file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(
            destination_dir, message_dispatcher=self.message_dispatcher)

        # ------------- Create BTO ------------- #
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 4: Downloading data file")
        self.log_info_message("-" * 60)
        self.log_info_message("Downloading bto.owl...")
        bto_file_path = file_downloader.download_file_if_missing(
            params["bto_file"], filename="bto.owl")
        self.log_info_message("✓ bto.owl downloaded")

        self.log_info_message("-" * 60)
        self.log_info_message("STEP 5: Populating database")
        self.log_info_message("-" * 60)

        BTOService.create_bto_db(destination_dir, bto_file_path, self.message_dispatcher)

        self.log_info_message("✓ Database population completed")

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        try:
            final_bto_count = BTO.select().count()
            final_ancestor_count = BTOAncestor.select().count()
            self.log_info_message(f"Final - BTO: {final_bto_count}, BTOAncestor: {final_ancestor_count} records")
        except Exception as e:
            self.log_info_message(f"Could not get final counts: {e}")

        self.log_info_message("=" * 60)
        self.log_info_message("BTO DATABASE CREATOR - COMPLETED")
        self.log_info_message("=" * 60)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)
