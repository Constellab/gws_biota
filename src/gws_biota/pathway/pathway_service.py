

from gws_core import Logger, MessageDispatcher

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.reactome import Reactome as ReactomeHelper
from ..base.base_service import BaseService
from .pathway import Pathway, PathwayAncestor
from .pathway_compound import PathwayCompound


class PathwayService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_pathway_db(cls, path, pwo_file, reactome_pathways_file, reactome_pathway_relations_file,
                          reactome_chebi_pathways_file, message_dispatcher: MessageDispatcher = None):
        """
        Creates and fills the `pwo` database

        :params: path of the files
        :type: str
        :returns: None
        :rtype: None
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("STARTING PATHWAY DATABASE CREATION")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("Starting pathway database creation...")

        cls._log_table_states("BEFORE CREATION")

        # insert pathways
        Logger.info("-" * 80)
        Logger.info("STEP 1: Parsing and inserting pathways")
        Logger.info("-" * 80)
        message_dispatcher.notify_info_message("Step 1: Parsing pathways...")
        pathway_dict = ReactomeHelper.parse_pathways_to_dict(
            path, reactome_pathways_file)
        Logger.info(f"Parsed {len(pathway_dict)} pathways from file")
        message_dispatcher.notify_info_message(f"Parsed {len(pathway_dict)} pathways")

        pathways = []
        for _pw in pathway_dict:
            pw = Pathway(
                name=_pw["name"],
                reactome_pathway_id=_pw["reactome_pathway_id"],
                data={
                    # "name": _pw["name"],
                    "species": _pw["species"]
                }
            )
            ft_names = [pw.name]
            pw.ft_names = cls.format_ft_names(ft_names)
            pathways.append(pw)

        Logger.info(f"Creating {len(pathways)} pathway records...")
        Pathway.create_all(pathways)
        Logger.info(f"✓ Successfully created {len(pathways)} pathway records")
        message_dispatcher.notify_info_message(f"✓ Created {len(pathways)} pathway records")

        cls._log_table_states("AFTER PATHWAY INSERTION")

        # insert pathways ancestors
        Logger.info("-" * 80)
        Logger.info("STEP 2: Parsing and inserting pathway ancestors")
        Logger.info("-" * 80)
        message_dispatcher.notify_info_message("Step 2: Processing pathway relationships...")
        pathway_rels = ReactomeHelper.parse_pathway_relations_to_dict(
            path, reactome_pathway_relations_file)
        Logger.info(f"Parsed {len(pathway_rels)} pathway relations from file")

        vals = cls.__query_vals_of_ancestors(pathway_rels)
        Logger.info(f"Generated {len(vals)} ancestor relationship records")

        # Check and remove duplicates
        vals_deduplicated = cls._check_and_remove_duplicates(vals)
        Logger.info(f"After deduplication: {len(vals_deduplicated)} records to insert")

        if vals_deduplicated:
            Logger.info("Inserting pathway ancestor relationships...")
            PathwayAncestor.insert_all(vals_deduplicated)
            Logger.info(f"✓ Successfully inserted {len(vals_deduplicated)} ancestor relationships")
            message_dispatcher.notify_info_message(f"✓ Inserted {len(vals_deduplicated)} ancestor relationships")
        else:
            Logger.warning("⚠ No ancestor relationships to insert (all were duplicates or empty)")
            message_dispatcher.notify_info_message("⚠ No ancestor relationships to insert")

        cls._log_table_states("AFTER ANCESTOR INSERTION")

        # insert chebi pathways
        Logger.info("-" * 80)
        Logger.info("STEP 3: Parsing and inserting pathway compounds")
        Logger.info("-" * 80)
        message_dispatcher.notify_info_message("Step 3: Processing pathway-compound associations...")
        chebi_pathways = ReactomeHelper.parse_chebi_pathway_to_dict(
            path, reactome_chebi_pathways_file)
        Logger.info(f"Parsed {len(chebi_pathways)} pathway-compound associations from file")

        pathways_comps = []
        for cpw in chebi_pathways:
            chebi_id = "CHEBI:"+cpw["chebi_id"]
            pc = PathwayCompound(
                chebi_id=chebi_id,
                reactome_pathway_id=cpw["reactome_pathway_id"],
                species=cpw["species"]
            )
            pathways_comps.append(pc)

        Logger.info(f"Creating {len(pathways_comps)} pathway-compound records...")
        PathwayCompound.create_all(pathways_comps)
        Logger.info(f"✓ Successfully created {len(pathways_comps)} pathway-compound records")
        message_dispatcher.notify_info_message(f"✓ Created {len(pathways_comps)} pathway-compound records")

        cls._log_table_states("AFTER COMPOUND INSERTION")

        Logger.info("=" * 80)
        Logger.info("PATHWAY DATABASE CREATION COMPLETED SUCCESSFULLY")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ Pathway database creation completed successfully!")

    @classmethod
    def __query_vals_of_ancestors(cls, pathway_rels):
        Logger.info("Building ancestor relationship queries...")
        vals = []
        missing_count = 0

        for idx, _pw in enumerate(pathway_rels):
            try:
                pathway_id = Pathway.get(
                    Pathway.reactome_pathway_id == _pw["reactome_pathway_id"]).id
                ancestor_id = Pathway.get(
                    Pathway.reactome_pathway_id == _pw["ancestor"]).id
                val = {'pathway': pathway_id, 'ancestor': ancestor_id}
                vals.append(val)

                if (idx + 1) % 100 == 0:
                    Logger.info(f"  Processed {idx + 1}/{len(pathway_rels)} relations...")
            except Exception as e:
                missing_count += 1
                if missing_count <= 5:  # Log first 5 missing relations
                    Logger.debug(f"  Skipping relation (pathway not found): {_pw.get('reactome_pathway_id')} -> {_pw.get('ancestor')}")

        if missing_count > 0:
            Logger.info(f"  Skipped {missing_count} relations (referenced pathways not found in database)")

        return vals

    @classmethod
    def _check_and_remove_duplicates(cls, vals):
        """
        Check for duplicates and remove them, returning only unique records

        :param vals: List of dictionaries with 'pathway' and 'ancestor' keys
        :return: List of unique records
        """
        Logger.info("Checking for duplicate ancestor relationships...")

        seen_combinations = set()
        unique_vals = []
        duplicates = []

        for item in vals:
            combination = (item['pathway'], item['ancestor'])
            if combination in seen_combinations:
                duplicates.append(item)
            else:
                seen_combinations.add(combination)
                unique_vals.append(item)

        if duplicates:
            Logger.warning(f"⚠ Found {len(duplicates)} DUPLICATE ancestor relationships!")
            Logger.warning("First 5 duplicates:")
            for i, duplicate in enumerate(duplicates[:5]):
                Logger.warning(f"  [{i+1}] pathway_id={duplicate['pathway']}, ancestor_id={duplicate['ancestor']}")
            if len(duplicates) > 5:
                Logger.warning(f"  ... and {len(duplicates) - 5} more duplicates")
        else:
            Logger.info("✓ No duplicates found in ancestor relationships")

        return unique_vals

    @classmethod
    def _log_table_states(cls, stage: str):
        """Log the current state of pathway-related tables"""
        try:
            Logger.info(f"--- TABLE STATES: {stage} ---")

            pathway_count = Pathway.select().count()
            Logger.info(f"  Pathway table: {pathway_count} records")

            try:
                ancestor_count = PathwayAncestor.select().count()
                Logger.info(f"  PathwayAncestor table: {ancestor_count} records")
            except Exception as e:
                Logger.info(f"  PathwayAncestor table: Not accessible ({type(e).__name__})")

            try:
                compound_count = PathwayCompound.select().count()
                Logger.info(f"  PathwayCompound table: {compound_count} records")
            except Exception as e:
                Logger.info(f"  PathwayCompound table: Not accessible ({type(e).__name__})")

            Logger.info("-" * 60)
        except Exception as e:
            Logger.warning(f"  Could not log table states: {e}")
