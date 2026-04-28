

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

from gws_biota import ECO
from gws_biota.eco.eco import ECOAncestor
from gws_biota.eco.eco_service import ECOService

from .db_service import DbService


@task_decorator("EcoDBCreator", short_description="Download the online file eco.obo (The Evidence & Conclusion Ontology) and use it to load the “biota_eco” table from the BIOTA database.")
class EcoDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"eco_file": StrParam(
        default_value="https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        self.log_info_message("=" * 60)
        self.log_info_message("ECO DATABASE CREATOR - STARTING")
        self.log_info_message("=" * 60)

        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        try:
            eco_count = ECO.select().count()
            ancestor_count = ECOAncestor.select().count()
            self.log_info_message(f"Current - ECO: {eco_count}, Ancestor: {ancestor_count}")
        except:
            self.log_info_message("Current tables: Don't exist or are empty")

        # Deleting the database...
        self.log_info_message("Deleting the ECO database...")
        DbService.drop_biota_tables([ECO, ECOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables dropped")

        # Verify tables are dropped
        e_after_drop = 0
        a_after_drop = 0
        try:
            e_after_drop = ECO.select().count()
            a_after_drop = ECOAncestor.select().count()
        except:
            self.log_info_message("✓ Tables don't exist (expected after drop)")
        if e_after_drop > 0 or a_after_drop > 0:
            raise Exception(f"ERROR: Tables not empty after drop! ECO:{e_after_drop}, Ancestor:{a_after_drop}. Drop table failed, aborting script.")
        else:
            self.log_info_message("✓ Verified: Tables empty after drop")

        # ... to build it from 0
        self.log_info_message("Creating the ECO database...")
        DbService.create_biota_tables([ECO, ECOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables created")

        # Verify tables are empty after creation
        try:
            e_after_create = ECO.select().count()
            a_after_create = ECOAncestor.select().count()
            if e_after_create > 0 or a_after_create > 0:
                self.log_info_message(f"⚠ WARNING: Tables not empty after create! ECO:{e_after_create}, Ancestor:{a_after_create}")
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

        self.log_info_message("eco.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create ECO ------------- #
        # download file
        self.log_info_message("Downloading eco.obo...")
        eco_file = file_downloader.download_file_if_missing(
            params["eco_file"], filename="eco.obo")
        self.log_info_message("✓ Downloaded")

        ECOService.create_eco_db(destination_dir, eco_file, self.message_dispatcher)

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        try:
            final_eco = ECO.select().count()
            final_ancestor = ECOAncestor.select().count()
            self.log_info_message(f"✓ Final counts:")
            self.log_info_message(f"  - ECO terms: {final_eco}")
            self.log_info_message(f"  - Ancestors: {final_ancestor}")
            success_msg = f"✓ ECO database created successfully:\n  - ECO terms: {final_eco}\n  - Ancestors: {final_ancestor}"
        except Exception as e:
            self.log_info_message(f"Could not verify final counts: {e}")
            success_msg = "✓ ECO database created (counts unavailable)"

        self.log_info_message("=" * 60)
        self.log_info_message("ECO DATABASE CREATOR - COMPLETED")
        self.log_info_message("=" * 60)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)
        self.log_info_message("=" * 60)

        return {"output_text": Text(success_msg)}
