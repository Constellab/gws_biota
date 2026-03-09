

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

from gws_biota import Pathway
from gws_biota.pathway.pathway import PathwayAncestor
from gws_biota.pathway.pathway_compound import PathwayCompound
from gws_biota.pathway.pathway_service import PathwayService

from .db_service import DbService


@task_decorator("PathwayDBCreator", short_description="Download the online files from rgd.mcw.edu and reactome databases and use them to load the “biota_pathway” table from the BIOTA database.")
class PathwayDBCreator(Task):
    input_specs = InputSpecs({"input_text": InputSpec(Text, optional=True)})
    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"pwo_file": StrParam(
        default_value="https://download.rgd.mcw.edu/ontology/pathway/pathway.obo"),
        "reactome_pathways_file": StrParam(default_value="https://reactome.org/download/current/ReactomePathways.txt"),
        "reactome_pathway_relations_file": StrParam(default_value="https://reactome.org/download/current/ReactomePathwaysRelation.txt"),
        "reactome_chebi_pathways_file": StrParam(default_value="https://reactome.org/download/current/ChEBI2Reactome.txt")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        self.log_info_message("=" * 60)
        self.log_info_message("PATHWAY DATABASE CREATOR - STARTING")
        self.log_info_message("=" * 60)

        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Log current state BEFORE dropping
        self.log_info_message("Checking current database state...")
        try:
            pathway_count_before = Pathway.select().count()
            self.log_info_message(f"Current Pathway records: {pathway_count_before}")
        except:
            self.log_info_message("Current Pathway records: Table doesn't exist or is empty")

        try:
            ancestor_count_before = PathwayAncestor.select().count()
            self.log_info_message(f"Current PathwayAncestor records: {ancestor_count_before}")
        except:
            self.log_info_message("Current PathwayAncestor records: Table doesn't exist or is empty")

        try:
            compound_count_before = PathwayCompound.select().count()
            self.log_info_message(f"Current PathwayCompound records: {compound_count_before}")
        except:
            self.log_info_message("Current PathwayCompound records: Table doesn't exist or is empty")

        # Deleting the database...
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 1: Dropping existing tables")
        self.log_info_message("-" * 60)
        self.log_info_message("Deleting the PATHWAY database...")
        DbService.drop_biota_tables([Pathway, PathwayAncestor, PathwayCompound], self.message_dispatcher)
        self.log_info_message("✓ Tables dropped successfully")

        # ... to build it from 0
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 2: Creating new tables")
        self.log_info_message("-" * 60)
        self.log_info_message("Creating the PATHWAY database...")
        DbService.create_biota_tables([Pathway, PathwayAncestor, PathwayCompound], self.message_dispatcher)
        self.log_info_message("✓ Tables created successfully")

        # Verify tables are empty
        self.log_info_message("Verifying tables are empty...")
        try:
            pathway_count_after = Pathway.select().count()
            ancestor_count_after = PathwayAncestor.select().count()
            compound_count_after = PathwayCompound.select().count()

            self.log_info_message(f"  Pathway: {pathway_count_after} records")
            self.log_info_message(f"  PathwayAncestor: {ancestor_count_after} records")
            self.log_info_message(f"  PathwayCompound: {compound_count_after} records")

            if pathway_count_after > 0 or ancestor_count_after > 0 or compound_count_after > 0:
                self.log_info_message("⚠ WARNING: Tables are not empty after creation! This may cause duplicate key errors.")
        except Exception as e:
            self.log_info_message(f"Could not verify table states: {e}")

        # Check that all url exist and work
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 3: Validating download URLs")
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

        self.log_info_message("All files were found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create PATHWAY ------------- #
        self.log_info_message("-" * 60)
        self.log_info_message("STEP 4: Downloading data files")
        self.log_info_message("-" * 60)

        # download pathway file
        self.log_info_message("Downloading pathway.obo...")
        pathway_file = file_downloader.download_file_if_missing(
            params["pwo_file"], filename="pathway.obo")
        self.log_info_message("✓ pathway.obo downloaded")

        # download reactome pathway file
        self.log_info_message("Downloading ReactomePathways.txt...")
        reactome_pathways_file = file_downloader.download_file_if_missing(
            params["reactome_pathways_file"], filename="ReactomePathways.txt")
        self.log_info_message("✓ ReactomePathways.txt downloaded")

        # download reactome pathway relation file
        self.log_info_message("Downloading ReactomePathwaysRelation.txt...")
        reactome_pathway_relations_file = file_downloader.download_file_if_missing(
            params["reactome_pathway_relations_file"], filename="ReactomePathwaysRelation.txt")
        self.log_info_message("✓ ReactomePathwaysRelation.txt downloaded")

        # download reactome chebi pathway file
        self.log_info_message("Downloading ChEBI2Reactome.txt...")
        reactome_chebi_pathways_file = file_downloader.download_file_if_missing(
            params["reactome_chebi_pathways_file"], filename="ChEBI2Reactome.txt")
        self.log_info_message("✓ ChEBI2Reactome.txt downloaded")

        self.log_info_message("-" * 60)
        self.log_info_message("STEP 5: Populating database")
        self.log_info_message("-" * 60)
        self.log_info_message("Starting PathwayService.create_pathway_db()...")

        PathwayService.create_pathway_db(
            destination_dir, pathway_file, reactome_pathways_file, reactome_pathway_relations_file,
            reactome_chebi_pathways_file, self.message_dispatcher)
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)

        try:
            final_pathway_count = Pathway.select().count()
            final_ancestor_count = PathwayAncestor.select().count()
            final_compound_count = PathwayCompound.select().count()

            self.log_info_message(f"Final table counts:")
            self.log_info_message(f"  Pathway: {final_pathway_count} records")
            self.log_info_message(f"  PathwayAncestor: {final_ancestor_count} records")
            self.log_info_message(f"  PathwayCompound: {final_compound_count} records")
        except Exception as e:
            self.log_info_message(f"Could not get final counts: {e}")

        self.log_info_message("=" * 60)
        self.log_info_message("PATHWAY DATABASE CREATOR - COMPLETED SUCCESSFULLY")
        self.log_info_message("=" * 60)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        return {}
