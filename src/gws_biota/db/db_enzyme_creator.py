
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

        # Check that dependent databases are available before downloading enzyme data.
        len_bto = BTO.select().count()
        len_taxonomy = Taxonomy.select().count()
        len_pathway = Pathway.select().count()

        if len_bto == 0 or len_taxonomy == 0 or len_pathway == 0:
            raise Exception(
                "No data from the TAXONOMY, BTO or PATHWAY databases available in Biota. Please update these databases before the ENZYME database.")

        # Deleting the database...
        self.log_info_message("Deleting the ENZYME database...")
        DbService.drop_biota_tables([Enzyme])

        # ... to build it from 0
        self.log_info_message("Creating the ENZYME database...")
        DbService.create_biota_tables([Enzyme])

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
            # Try to download from URL first
            bkms_file = file_downloader.download_file_if_missing(
                params["bkms_file"], filename="Reactions_BKMS.tar.gz", decompress_file=True)
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

        # download TAXONOMY file
        taxdump_files = file_downloader.download_file_if_missing(
            params["taxdump_files"], filename="taxdump.tar.gz", decompress_file=True)

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

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)
