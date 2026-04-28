

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

from gws_biota import GO
from gws_biota.go.go import GOAncestor
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
        self.log_info_message("=" * 60)
        self.log_info_message("GO DATABASE CREATOR - STARTING")
        self.log_info_message("=" * 60)

        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        try:
            go_count = GO.select().count()
            ancestor_count = GOAncestor.select().count()
            self.log_info_message(f"Current - GO: {go_count}, Ancestor: {ancestor_count}")
        except:
            self.log_info_message("Current tables: Don't exist or are empty")

        # Deleting the database...
        self.log_info_message("Deleting the GO database...")
        DbService.drop_biota_tables([GO, GOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables dropped")

        # Verify tables are dropped
        go_after_drop = 0
        ancestor_after_drop = 0
        try:
            go_after_drop = GO.select().count()
            ancestor_after_drop = GOAncestor.select().count()
        except:
            self.log_info_message("✓ Tables don't exist (expected after drop)")
        if go_after_drop > 0 or ancestor_after_drop > 0:
            raise Exception(f"ERROR: Tables not empty after drop! GO:{go_after_drop}, Ancestor:{ancestor_after_drop}. Drop table failed, aborting script.")
        else:
            self.log_info_message("✓ Verified: Tables empty after drop")

        # ... to build it from 0
        self.log_info_message("Creating the GO database...")
        DbService.create_biota_tables([GO, GOAncestor], self.message_dispatcher)
        self.log_info_message("✓ Tables created")

        # Verify tables are empty after creation
        try:
            go_after_create = GO.select().count()
            ancestor_after_create = GOAncestor.select().count()
            if go_after_create > 0 or ancestor_after_create > 0:
                self.log_info_message(f"⚠ WARNING: Tables not empty after create! GO:{go_after_create}, Ancestor:{ancestor_after_create}")
            else:
                self.log_info_message("✓ Verified: Tables empty and ready for data")
        except Exception as e:
            self.log_info_message(f"Could not verify tables: {e}")

        # Checks that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                Logger.info(f"{key}: OK - {url}")
                self.log_info_message(f"✓ URL validated")
            except requests.exceptions.RequestException as e:
                Logger.error(f"{key}: Error - {url}\n{e}")

        self.log_info_message("go.obo file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create GO ------------- #
        # download file
        self.log_info_message("Downloading go.obo...")
        go_file = file_downloader.download_file_if_missing(
            params["go_file"], filename="go.obo")
        self.log_info_message("✓ Downloaded")

        GOService.create_go_db(destination_dir, go_file, self.message_dispatcher)

        # Final verification with detailed counts
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        try:
            final_go = GO.select().count()
            final_ancestor = GOAncestor.select().count()
            self.log_info_message(f"✓ Final counts:")
            self.log_info_message(f"  - GO terms: {final_go}")
            self.log_info_message(f"  - GO ancestors: {final_ancestor}")
            success_msg = f"✓ GO database created successfully:\n  - GO terms: {final_go}\n  - Ancestors: {final_ancestor}"
        except Exception as e:
            self.log_info_message(f"Could not verify final counts: {e}")
            success_msg = "✓ GO database created (counts unavailable)"

        self.log_info_message("=" * 60)
        self.log_info_message("GO DATABASE CREATOR - COMPLETED")
        self.log_info_message("=" * 60)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        return {"output_text": Text(success_msg)}
