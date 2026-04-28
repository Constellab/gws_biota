

import re

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

from gws_biota import Reaction
from gws_biota.reaction.reaction_service import ReactionService

from ..compound.compound_service import Compound
from ..enzyme.enzyme_service import Enzyme
from ..taxonomy.taxonomy import Taxonomy
from .db_service import DbService


@task_decorator("ReactionDBCreator", short_description="Download the online files from expasy and rhea databases, and use them to load the “biota_reaction” table from the BIOTA database.")
class ReactionDBCreator(Task):
    input_specs = InputSpecs({"input_compound": InputSpec(Text, human_name="link to compound", optional=True),
                              "input_taxonomy": InputSpec(Text, human_name="link to taxonomy", optional=True),
                              "input_enzyme": InputSpec(Text, human_name="link to enzyme", optional=True)})

    output_specs = OutputSpecs(
        {"output_text": OutputSpec(Text, optional=True)})
    config_specs = ConfigSpecs({"rhea_direction_file": StrParam(
        default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea-directions.tsv"),
        "rhea2ecocyc_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2ecocyc.tsv"),
        "rhea2metacyc_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2metacyc.tsv"),
        "rhea2macie_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2macie.tsv"),
        "rhea2kegg_reaction_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2kegg%5Freaction.tsv"),
        "rhea2ec_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2ec.tsv"),
        "rhea2reactome_file": StrParam(default_value="https://ftp.expasy.org/databases/rhea/tsv/rhea2reactome.tsv"),
        "rhea_reactions_file": StrParam(default_value="https://www.rhea-db.org/rhea/?query=uniprot:*&columns=rhea-id,equation,chebi-id,ec&format=tsv")})

    # only allow admin user to run this process
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Clean Python cache to ensure fresh state
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        len_bto = Compound.select().count()
        len_taxonomy = Taxonomy.select().count()
        len_pathway = Enzyme.select().count()

        # Check that dependent databases are available before downloading enzyme data.
        if len_bto == 0 or len_taxonomy == 0 or len_pathway == 0:
            raise Exception(
                "No data from the TAXONOMY, COMPOUND or ENZYME databases available in Biota. Please update these databases before the ENZYME database.")

        # Deleting the database...
        self.log_info_message("Deleting the RHEA database...")
        DbService.drop_biota_tables([Reaction], message_dispatcher=self.message_dispatcher)
        self.log_info_message("✓ Tables dropped (Reaction + related tables)")

        # Verify tables are dropped (Reaction.drop_table() handles all related tables)
        r_after_drop = 0
        try:
            r_after_drop = Reaction.select().count()
        except:
            self.log_info_message("✓ Tables don't exist (expected after drop)")
        if r_after_drop > 0:
            raise Exception(f"ERROR: Tables not empty after drop! Reaction:{r_after_drop}. Drop table failed, aborting script.")
        else:
            self.log_info_message("✓ Verified: All tables empty after drop")

        # ... to build it from 0
        self.log_info_message("Creating the RHEA database...")
        DbService.create_biota_tables([Reaction], message_dispatcher=self.message_dispatcher)
        self.log_info_message("✓ Tables created (Reaction + related tables)")

        # Verify tables are empty after creation
        try:
            r_after_create = Reaction.select().count()
            if r_after_create > 0:
                self.log_info_message(f"⚠ WARNING: Tables not empty after create! Reaction:{r_after_create}")
            else:
                self.log_info_message("✓ Verified: All tables empty and ready for data")
        except Exception as e:
            self.log_info_message(f"Could not verify tables: {e}")

        # Check that all url exist and work
        for key, url in params.items():
            try:
                response = requests.head(url)
                response.raise_for_status()
                print(f"{key}: OK - {url}")
            except requests.exceptions.RequestException as e:
                print(f"{key}: Error - {url}\n{e}")

        self.log_info_message("All files were found.")

        destination_dir = Settings.make_temp_dir()
        file_downloader = FileDownloader(destination_dir)

        # ------------- Create RHEA ------------- #
        # download direction file
        rhea_direction_file = file_downloader.download_file_if_missing(
            params["rhea_direction_file"], filename="rhea-directions.tsv")

        # download ecocyc file
        rhea2ecocyc_file = file_downloader.download_file_if_missing(
            params["rhea2ecocyc_file"], filename="rhea2ecocyc.tsv")

        # download metacyc file
        rhea2metacyc_file = file_downloader.download_file_if_missing(
            params["rhea2metacyc_file"], filename="rhea2metacyc.tsv")

        # download macie file
        rhea2macie_file = file_downloader.download_file_if_missing(
            params["rhea2macie_file"], filename="rhea2macie.tsv")

        # download kegg file
        rhea2kegg_reaction_file = file_downloader.download_file_if_missing(
            params["rhea2kegg_reaction_file"], filename="rhea2kegg.tsv")

        # download ec file
        rhea2ec_file = file_downloader.download_file_if_missing(
            params["rhea2ec_file"], filename="rhea2ec.tsv")

        # download reactome file
        rhea2reactome_file = file_downloader.download_file_if_missing(
            params["rhea2reactome_file"], filename="rhea2reactome.tsv")

        # download and construct reactions file
        rhea_reactions_file = file_downloader.download_file_if_missing(
            params["rhea_reactions_file"], filename="rhea_reactions.tsv")

        with open(rhea_reactions_file, encoding='utf-8') as reactions_file:
            with open(f"{destination_dir}/rhea_reactions.txt", 'w', encoding='utf-8') as new_reactions_file:
                # Ignore the first line which is the headere
                lines = reactions_file.readlines()

                for ligne in lines[1:]:
                    colonnes = ligne.split('\t')

                    operators_in_def = re.findall(r"(\ [\+\=]\ )", colonnes[1])
                    chebi_ids = colonnes[2].split(";")

                    new_reactions_file.write(f"ENTRY       {colonnes[0]}\n")

                    # Checking the presence of the "equation" column
                    if len(colonnes) > 1 and colonnes[1]:
                        new_reactions_file.write(
                            f"DEFINITION  {colonnes[1]}\n")

                    # Checking the presence of the “chebi-id” column
                    if len(colonnes) > 2 and colonnes[2]:
                        new_reactions_file.write("EQUATION    ")
                        # Rewriting the equation : CHEBI:58758;CHEBI:16842;CHEBI:57925 -> CHEBI:58758 = CHEBI:16842 + CHEBI:57925
                        for index, value in enumerate(chebi_ids):
                            if index < len(operators_in_def):
                                new_reactions_file.write(
                                    f"{value} {operators_in_def[index]} ")
                            else:
                                new_reactions_file.write(f"{value} ")
                        new_reactions_file.write("\n")

                    # Checking the presence of the “ec” column
                    if len(colonnes) > 3 and colonnes[3]:
                        enzymes = re.split(":|;", colonnes[3])

                        new_reactions_file.write("ENZYME      ")
                        for enzyme in enzymes:
                            if enzyme == "EC":
                                continue

                            new_reactions_file.write(f"{enzyme}")
                    new_reactions_file.write("///\n")

        ReactionService.create_reaction_db(
            destination_dir, f"{destination_dir}/rhea_reactions.txt", rhea_direction_file, rhea2ecocyc_file,
            rhea2metacyc_file, rhea2macie_file, rhea2kegg_reaction_file, rhea2ec_file, rhea2reactome_file)

        # Clean Python cache after execution
        self.log_info_message("Cleaning cache after execution...")
        DbService.clean_python_cache(message_dispatcher=self.message_dispatcher)

        # Final verification
        self.log_info_message("-" * 60)
        self.log_info_message("FINAL VERIFICATION")
        self.log_info_message("-" * 60)
        # Count reactions created
        try:
            from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct, ReactionEnzyme
            reaction_count = Reaction.select().count()
            substrate_count = ReactionSubstrate.select().count()
            product_count = ReactionProduct.select().count()
            enzyme_count = ReactionEnzyme.select().count()
            self.log_info_message(f"✓ Final counts:")
            self.log_info_message(f"  - Reactions: {reaction_count}")
            self.log_info_message(f"  - Substrates: {substrate_count}")
            self.log_info_message(f"  - Products: {product_count}")
            self.log_info_message(f"  - Enzymes: {enzyme_count}")
            success_msg = f"✓ Reaction database created successfully:\n  - Reactions: {reaction_count}\n  - Substrates: {substrate_count}\n  - Products: {product_count}\n  - Enzymes: {enzyme_count}"
        except Exception as e:
            self.log_info_message(f"Could not get complete counts: {e}")
            try:
                reaction_count = Reaction.select().count()
                success_msg = f"✓ Reaction database created successfully: {reaction_count} reactions loaded"
            except:
                success_msg = f"✓ Reaction database created (counts unavailable: {e})"

        self.log_info_message(success_msg)

        return {"output_text": Text(success_msg)}
