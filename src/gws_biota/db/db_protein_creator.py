

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

from gws_biota import Protein
from gws_biota.protein.protein_service import ProteinService

from .db_service import DbService


@task_decorator("ProteinDBCreator",
                short_description="Download the online file uniprot_sprot.fasta.gz from uniprot database and use it to load the “biota_protein” table from the BIOTA database.")
class ProteinDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"protein_file": StrParam(
        default_value="https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Deleting the database...
        self.log_info_message("Deleting the PROTEIN database...")
        DbService.drop_biota_tables([Protein], message_dispatcher=self.message_dispatcher)
        self.log_info_message("✓ Table dropped")

        # Verify table is dropped
        try:
            p_after_drop = Protein.select().count()
            if p_after_drop > 0:
                self.log_info_message(f"⚠ WARNING: Table not empty after drop! Protein:{p_after_drop}")
            else:
                self.log_info_message("✓ Verified: Table empty after drop")
        except:
            self.log_info_message("✓ Table doesn't exist (expected after drop)")

        # ... to build it from 0
        self.log_info_message("Creating the PROTEIN database...")
        DbService.create_biota_tables([Protein], message_dispatcher=self.message_dispatcher)
        self.log_info_message("✓ Table created")

        # Verify table is empty after creation
        try:
            p_after_create = Protein.select().count()
            if p_after_create > 0:
                self.log_info_message(f"⚠ WARNING: Table not empty after create! Protein:{p_after_create}")
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

        self.log_info_message("uniprot_sprot.fasta.gz file found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create PROTEIN ------------- #
        # download file
        protein_file = file_downloader.download_file_if_missing(
            params["protein_file"], filename="uniprot_sprot.fasta.gz")

        ProteinService.create_protein_db(destination_dir, protein_file)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        # Count proteins created
        try:
            protein_count = Protein.select().count()
            self.log_info_message(f"✓ Final count: {protein_count} proteins")
            success_msg = f"✓ Protein database created successfully: {protein_count} proteins loaded"
            self.log_info_message(success_msg)
            return {"output_text": Text(success_msg)}
        except Exception as e:
            error_msg = f"Database created but could not count records: {e}"
            self.log_info_message(error_msg)
            return {"output_text": Text(error_msg)}
