
import gzip
import os
import tarfile
import requests
from gws_core import (
    ConfigParams,
    ConfigSpecs,
    File,
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

from gws_biota import Enzyme
from gws_biota.enzyme.deprecated_enzyme import DeprecatedEnzyme
from gws_biota.enzyme.enzyme import EnzymeBTO
from gws_biota.enzyme.enzyme_class import EnzymeClass
from gws_biota.enzyme.enzyme_ortholog import EnzymeOrtholog
from gws_biota.enzyme.enzyme_pathway import EnzymePathway
from gws_biota.enzyme.enzyme_service import EnzymeService

from ..bto.bto import BTO
from ..pathway.pathway import Pathway
from ..taxonomy.taxonomy import Taxonomy
from .db_service import DbService


@task_decorator("EnzymeDBCreator", short_description="Download the online folders/files from BRENDA, ebi.ac.uk and ncbi databases and use them to load the “biota_enzyme” table from the BIOTA database.")
class EnzymeDBCreator(Task):
    input_specs = InputSpecs({'input_brenda': InputSpec(File, human_name="Enzyme file",
                             short_description="Enzyme file from BRENDA database"),
                             "input_bto": InputSpec(Text, human_name="link to bto", optional=True),
                              "input_taxonomy": InputSpec(Text, human_name="link to taxonomy", optional=True),
                              "input_protein": InputSpec(Text, human_name="link to protein", optional=True)})

    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"bkms_file": StrParam(default_value="https://bkms.brenda-enzymes.org/download/Reactions_BKMS.tar.gz"), "expasy_file": StrParam(
        default_value="https://raw.githubusercontent.com/google-research/proteinfer/540773f988005cc5ed834210d1477e4db1f141e6/testdata/enzclass.txt"),
        "compound_file": StrParam(default_value="https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo"),
        "bto_file": StrParam(default_value="https://raw.githubusercontent.com/BRENDA-Enzymes/BTO/master/bto.owl"),
        "taxdump_files": StrParam(default_value="https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        input_file: File = inputs["input_brenda"]

        # Clean Python cache to ensure we start fresh and avoid conflicts/duplicates
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Ensure pigz is installed (required by gws_core FileDownloader for .tar.gz)
        DbService.ensure_pigz_installed()

        # Check that dependent databases are available before downloading enzyme data.
        len_bto = BTO.select().count()
        len_taxonomy = Taxonomy.select().count()
        len_pathway = Pathway.select().count()

        if len_bto == 0 or len_taxonomy == 0 or len_pathway == 0:
            raise Exception(
                "No data from the TAXONOMY, BTO or PATHWAY databases available in Biota. Please update these databases before the ENZYME database.")

        # Deleting the enzyme database tables...
        # Order: Drop child tables before parent tables (reverse FK dependencies)
        self.log_info_message("Deleting the ENZYME database...")
        enzyme_tables_to_drop = [
            EnzymeBTO,           # Has FK to Enzyme and BTO
            Enzyme,              # Has FK to EnzymeOrtholog
            DeprecatedEnzyme,    # Independent
            EnzymeOrtholog,      # Has FK to EnzymePathway
            EnzymePathway,       # Has FK to Pathway (external)
            EnzymeClass          # Independent
        ]
        DbService.drop_biota_tables(enzyme_tables_to_drop, message_dispatcher=self.message_dispatcher)

        # Verify tables are dropped
        ez_after_drop = 0
        eo_after_drop = 0
        try:
            ez_after_drop = Enzyme.select().count()
            eo_after_drop = EnzymeOrtholog.select().count()
        except:
            self.log_info_message("✓ Tables don't exist (expected after drop)")
        if ez_after_drop > 0 or eo_after_drop > 0:
            raise Exception(f"ERROR: Tables not empty after drop! Enzyme:{ez_after_drop}, EnzymeOrtholog:{eo_after_drop}. Drop table failed, aborting script.")
        else:
            self.log_info_message("✓ Verified: Tables empty after drop")

        # Creating enzyme database tables from scratch...
        # Order: Create parent tables before child tables (follow FK dependencies)
        self.log_info_message("Creating the ENZYME database...")
        enzyme_tables_to_create = [
            EnzymeClass,         # Independent
            EnzymePathway,       # Depends on Pathway (external)
            EnzymeOrtholog,      # Depends on EnzymePathway
            Enzyme,              # Depends on EnzymeOrtholog
            DeprecatedEnzyme,    # Independent
            EnzymeBTO            # Depends on Enzyme and BTO
        ]
        DbService.create_biota_tables(enzyme_tables_to_create, message_dispatcher=self.message_dispatcher)

        # Check that all url exist and work
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                self.log_info_message(f"✓ {key}: {url}")
            except requests.exceptions.RequestException as e:
                if key == "bkms_file":
                    # BKMS is optional, just log a warning
                    self.log_warning_message(f"⚠ {key} not accessible (will be skipped): {url}")
                else:
                    # Other files are required
                    self.log_error_message(f"✗ {key}: Error - {url}\n{e}")
                    raise Exception(f"Required file {key} is not accessible: {url}")

        self.log_info_message("Required files verification completed.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(
            destination_dir, message_dispatcher=self.message_dispatcher)

        # ------------- Create ENZYME ------------- #
        # download BKMS file (optional - used to enrich pathway data)
        bkms_file = None
        local_bkms_path = "/lab/user/bricks/gws_biota/src/gws_biota/enzyme/Reactions_BKMS.tar.gz"

        try:
            # Try to download from URL first — decompress manually to avoid pigz dependency
            bkms_archive = file_downloader.download_file_if_missing(
                params["bkms_file"], filename="Reactions_BKMS.tar.gz", decompress_file=False)
            bkms_extract_dir = os.path.join(destination_dir, "Reactions_BKMS_extracted")
            os.makedirs(bkms_extract_dir, exist_ok=True)
            with tarfile.open(bkms_archive, "r:gz") as tar:
                tar.extractall(path=bkms_extract_dir)
            bkms_file = bkms_extract_dir
            self.log_info_message("✓ BKMS file downloaded successfully from URL")
        except Exception as e:
            self.log_warning_message(
                f"⚠ Could not download BKMS file from {params['bkms_file']}: {str(e)}")

            # Try to use local fallback file
            if os.path.exists(local_bkms_path):
                self.log_info_message(f"Using local BKMS file: {local_bkms_path}")
                try:
                    # Decompress tar.gz to temp directory
                    extract_dir = os.path.join(destination_dir, "Reactions_BKMS_extracted")
                    os.makedirs(extract_dir, exist_ok=True)

                    with tarfile.open(local_bkms_path, 'r:gz') as tar:
                        tar.extractall(path=extract_dir)

                    # Find the extracted CSV file
                    csv_file = os.path.join(extract_dir, "Reactions_BKMS.csv")
                    if os.path.exists(csv_file):
                        bkms_file = extract_dir
                        self.log_info_message(f"✓ Local BKMS file extracted successfully to {extract_dir}")
                    else:
                        self.log_warning_message(f"⚠ Could not find Reactions_BKMS.csv in extracted archive")
                        bkms_file = None
                except Exception as extract_error:
                    self.log_warning_message(f"⚠ Failed to extract local BKMS file: {str(extract_error)}")
                    bkms_file = None
            else:
                self.log_warning_message(f"⚠ Local BKMS file not found at {local_bkms_path}")

            if bkms_file is None:
                self.log_warning_message(
                    "Enzyme database will be created without BKMS pathway enrichment data")

        # download EXPASY file
        expasy_file = file_downloader.download_file_if_missing(
            params["expasy_file"], filename="enzclass.txt")

        # download TAXONOMY file — decompress manually with tarfile to avoid pigz dependency
        taxdump_archive = file_downloader.download_file_if_missing(
            params["taxdump_files"], filename="taxdump.tar.gz", decompress_file=False)

        extract_dir = os.path.join(destination_dir, "taxdump_extracted")
        os.makedirs(extract_dir, exist_ok=True)
        self.log_info_message("Extracting taxdump.tar.gz...")
        with tarfile.open(taxdump_archive, "r:gz") as tar:
            tar.extractall(path=extract_dir)
        taxdump_files = extract_dir
        self.log_info_message("✓ Extraction complete")

        # download BTO file
        bto_file = file_downloader.download_file_if_missing(
            params["bto_file"], filename="bto.owl")

        # download Compound File
        compound_file = file_downloader.download_file_if_missing(
            params["compound_file"], filename="chebi.obo")

        # Check if BRENDA file is compressed and decompress if needed
        brenda_file_path = input_file.path
        # Check magic bytes to detect gzip compression (0x1f 0x8b)
        with open(brenda_file_path, 'rb') as f:
            magic_bytes = f.read(2)

        if magic_bytes == b'\x1f\x8b':
            self.log_info_message("BRENDA file is gzip compressed, decompressing...")
            decompressed_path = os.path.join(destination_dir, "brenda_decompressed.txt")
            try:
                with gzip.open(brenda_file_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                brenda_file_path = decompressed_path
                self.log_info_message(f"✓ Decompressed BRENDA file to {decompressed_path}")
            except Exception as e:
                raise Exception(f"Failed to decompress BRENDA file: {str(e)}")
        else:
            self.log_info_message("BRENDA file is not compressed, using as-is")

        self.log_info_message("Creating enzyme database from downloaded files...")
        EnzymeService.create_enzyme_db(
            brenda_file=brenda_file_path, bkms_file=bkms_file, expasy_file=expasy_file, taxonomy_file=taxdump_files,
            bto_file=bto_file, compound_file=compound_file, message_dispatcher=self.message_dispatcher)

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        try:
            final_enzyme = Enzyme.select().count()
            final_class = EnzymeClass.select().count()
            final_pathway = EnzymePathway.select().count()
            final_ortholog = EnzymeOrtholog.select().count()
            final_deprecated = DeprecatedEnzyme.select().count()
            final_bto = EnzymeBTO.select().count()
            self.log_info_message(f"Final counts:")
            self.log_info_message(f"  - Enzymes: {final_enzyme}")
            self.log_info_message(f"  - EnzymeClasses: {final_class}")
            self.log_info_message(f"  - EnzymePathways: {final_pathway}")
            self.log_info_message(f"  - EnzymeOrthologs: {final_ortholog}")
            self.log_info_message(f"  - DeprecatedEnzymes: {final_deprecated}")
            self.log_info_message(f"  - EnzymeBTO: {final_bto}")
            success_msg = f"✓ Enzyme database created successfully:\n  - Enzymes: {final_enzyme}\n  - Classes: {final_class}\n  - Pathways: {final_pathway}\n  - Orthologs: {final_ortholog}\n  - Deprecated: {final_deprecated}\n  - BTO: {final_bto}"
        except Exception as e:
            self.log_info_message(f"Could not get final counts: {e}")
            success_msg = f"✓ Enzyme database created (counts unavailable: {e})"

        self.log_info_message("=" * 60)
        self.log_info_message("ENZYME DATABASE CREATOR - COMPLETED")
        self.log_info_message("=" * 60)
        # Check that no critical column is entirely NULL
        self.log_info_message("Checking for fully-NULL columns...")
        DbService.check_null_columns(Enzyme, ["ec_number", "name"], task_name="EnzymeDBCreator")
        self.log_info_message("✓ NULL column check passed")
        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        return {"output_text": Text(success_msg)}
