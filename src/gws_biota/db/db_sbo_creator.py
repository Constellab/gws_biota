

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

from gws_biota import SBO
from gws_biota.sbo.sbo import SBOAncestor
from gws_biota.sbo.sbo_service import SBOService

from .db_service import DbService


@task_decorator("SboDBCreator", short_description="Download the online file SBO_OBO.obo (Systems Biology Ontology) and use it to load the “biota_sbo” table from the BIOTA database.")
class SboDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"sbo_file": StrParam(
        default_value="https://raw.githubusercontent.com/EBI-BioModels/SBO/2143b2973f8912db9d4324a4fe543aabcd8f8ba7/SBO_OBO.obo")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        self.log_info_message("=" * 60)
        self.log_info_message("SBO DATABASE CREATOR - STARTING")
        self.log_info_message("=" * 60)

        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        try:
            sbo_count = SBO.select().count()
            ancestor_count = SBOAncestor.select().count()
            self.log_info_message(f"Current - SBO: {sbo_count}, Ancestor: {ancestor_count}")
        except:
            self.log_info_message("Current tables: Don't exist or are empty")

        # Deleting the database...
        self.log_info_message("Deleting the SBO database...")
        DbService.drop_biota_tables([SBO, SBOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables dropped")

        # Verify tables are dropped
        s_after_drop = 0
        a_after_drop = 0
        try:
            s_after_drop = SBO.select().count()
            a_after_drop = SBOAncestor.select().count()
        except:
            self.log_info_message("✓ Tables don't exist (expected after drop)")
        if s_after_drop > 0 or a_after_drop > 0:
            raise Exception(f"ERROR: Tables not empty after drop! SBO:{s_after_drop}, Ancestor:{a_after_drop}. Drop table failed, aborting script.")
        else:
            self.log_info_message("✓ Verified: Tables empty after drop")

        # ... to build it from 0
        self.log_info_message("Creating the SBO database...")
        DbService.create_biota_tables([SBO, SBOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables created")

        # Verify tables are empty after creation
        try:
            s_after_create = SBO.select().count()
            a_after_create = SBOAncestor.select().count()
            if s_after_create > 0 or a_after_create > 0:
                self.log_info_message(f"⚠ WARNING: Tables not empty after create! SBO:{s_after_create}, Ancestor:{a_after_create}")
            else:
                self.log_info_message("✓ Verified: Tables empty and ready for data")
        except Exception as e:
            self.log_info_message(f"Could not verify tables: {e}")

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                Logger.info(f"{key}: OK - {url}")
                self.log_info_message(f"✓ URL validated")
            except requests.exceptions.RequestException as e:
                Logger.error(f"{key}: Error - {url}\n{e}")

        self.log_info_message("sbo.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create SBO ------------- #
        # download file
        self.log_info_message("Downloading sbo.obo...")
        sbo_file = file_downloader.download_file_if_missing(
            params["sbo_file"], filename="sbo.obo")
        self.log_info_message("✓ Downloaded")

        SBOService.create_sbo_db(destination_dir, sbo_file, self.message_dispatcher)

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        try:
            final_sbo = SBO.select().count()
            final_ancestor = SBOAncestor.select().count()
            self.log_info_message(f"✓ Final counts:")
            self.log_info_message(f"  - SBO terms: {final_sbo}")
            self.log_info_message(f"  - Ancestors: {final_ancestor}")
            success_msg = f"✓ SBO database created successfully:\n  - SBO terms: {final_sbo}\n  - Ancestors: {final_ancestor}"
        except Exception as e:
            self.log_info_message(f"Could not verify final counts: {e}")
            success_msg = "✓ SBO database created (counts unavailable)"

        self.log_info_message("=" * 60)
        self.log_info_message("SBO DATABASE CREATOR - COMPLETED")
        self.log_info_message("=" * 60)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)
        self.log_info_message("=" * 60)

        return {"output_text": Text(success_msg)}
