

import os
import tarfile

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

from gws_biota import Taxonomy
from gws_biota.taxonomy.taxonomy_service import TaxonomyService

from .db_service import DbService


@task_decorator("TaxonomyDBCreator",
                short_description="Download the online file taxdump.tar.gz from ncbi and use it to load the “biota_taxonomy” table from the BIOTA database.")
class TaxonomyDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"taxdump_files": StrParam(
        default_value="https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Ensure pigz is installed (required by gws_core FileDownloader for .tar.gz)
        DbService.ensure_pigz_installed()

        # Deleting the database...
        self.log_info_message("Deleting the TAXONOMY database...")
        DbService.drop_biota_tables([Taxonomy], message_dispatcher=self.message_dispatcher)
        self.log_info_message("✓ Table dropped")

        # Verify table is dropped
        t_after_drop = 0
        try:
            t_after_drop = Taxonomy.select().count()
        except:
            self.log_info_message("✓ Table doesn't exist (expected after drop)")
        if t_after_drop > 0:
            raise Exception(f"ERROR: Table not empty after drop! Taxonomy:{t_after_drop}. Drop table failed, aborting script.")
        else:
            self.log_info_message("✓ Verified: Table empty after drop")

        # ... to build it from 0
        self.log_info_message("Creating the TAXONOMY database...")
        DbService.create_biota_tables([Taxonomy], message_dispatcher=self.message_dispatcher)
        self.log_info_message("✓ Table created")

        # Verify table is empty after creation
        try:
            t_after_create = Taxonomy.select().count()
            if t_after_create > 0:
                self.log_info_message(f"⚠ WARNING: Table not empty after create! Taxonomy:{t_after_create}")
            else:
                self.log_info_message("✓ Verified: Table empty and ready for data")
        except Exception as e:
            self.log_info_message(f"Could not verify table: {e}")

        # Check that the url exists and works
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("taxdump.tar.gz file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create TAXONOMY ------------- #
        # Download without decompression to avoid dependency on pigz (not always installed).
        # We decompress manually with Python's built-in tarfile module.
        archive_path = file_downloader.download_file_if_missing(
            params["taxdump_files"], filename="taxdump.tar.gz", decompress_file=False)

        extract_dir = os.path.join(destination_dir, "taxdump_extracted")
        os.makedirs(extract_dir, exist_ok=True)
        self.log_info_message("Extracting taxdump.tar.gz...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
        taxdump_files = extract_dir
        self.log_info_message("✓ Extraction complete")

        TaxonomyService.create_taxonomy_db(destination_dir, taxdump_files,
                                           message_dispatcher=self.message_dispatcher)

        # Clean Python cache after execution to ensure fresh state for next run
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        # Count taxonomies created
        try:
            taxonomy_count = Taxonomy.select().count()
            self.log_info_message(f"✓ Final count: {taxonomy_count} taxonomy entries")
            success_msg = f"✓ Taxonomy database created successfully: {taxonomy_count} taxonomy entries loaded"
            self.log_info_message(success_msg)
            # Check that no critical column is entirely NULL
            self.log_info_message("Checking for fully-NULL columns...")
            DbService.check_null_columns(
                Taxonomy,
                ["tax_id", "name", "rank", "division", "ancestor_tax_id"],
                task_name="TaxonomyDBCreator"
            )
            self.log_info_message("✓ NULL column check passed")
            return {"output_text": Text(success_msg)}
        except Exception as e:
            error_msg = f"Database created but could not count records: {e}"
            self.log_info_message(error_msg)
            return {"output_text": Text(error_msg)}
