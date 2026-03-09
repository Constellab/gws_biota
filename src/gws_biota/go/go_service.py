

from gws_core import Logger, MessageDispatcher

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from .go import GO, GOAncestor


class GOService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_go_db(cls, path, go_file, message_dispatcher: MessageDispatcher = None):
        """
        Creates and fills the `go` database

        :param path: path of the :file:`go.obo`
        :type path: str
        :param go_file: file that contains data file name
        :type go_file: file
        :returns: None
        :rtype: None
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("STARTING GO DATABASE CREATION")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("Starting GO database creation...")

        cls._log_table_states("BEFORE CREATION")

        Logger.info("-" * 80)
        Logger.info("STEP 1: Parsing and inserting GO terms")
        Logger.info("-" * 80)

        Logger.info("Loading GO file ...")
        onto_go = OntoHelper.create_ontology_from_file(path, go_file)
        list_go = OntoHelper.parse_obo_from_ontology(onto_go)
        Logger.info(f"Parsed {len(list_go)} GO terms from file")

        gos = [GO(data=dict_) for dict_ in list_go]

        Logger.info("Saving GO terms ...")
        for go in gos:
            go.set_go_id(go.data["id"])
            go.set_name(go.data["name"])
            go.set_namespace(go.data["namespace"])

            ft_names = [go.data["name"], go.data["id"].replace(":", "")]
            go.ft_names = cls.format_ft_names(ft_names)

            del go.data["id"]

        Logger.info(f"Creating {len(gos)} GO records...")
        GO.create_all(gos)
        Logger.info(f"✓ Successfully created {len(gos)} GO records")
        message_dispatcher.notify_info_message(f"✓ Created {len(gos)} GO records")

        cls._log_table_states("AFTER GO INSERTION")

        Logger.info("-" * 80)
        Logger.info("STEP 2: Inserting GO ancestor relationships")
        Logger.info("-" * 80)
        Logger.info("Saving GO ancestors ...")
        vals = []
        for go in gos:
            val = cls._get_ancestors_query(go)
            for v in val:
                vals.append(v)

        Logger.info(f"Generated {len(vals)} ancestor relationship records")

        # Deduplicate before insertion
        vals = cls._deduplicate_ancestor_vals(vals, 'go', 'ancestor')
        Logger.info(f"After deduplication: {len(vals)} records to insert")

        if vals:
            Logger.info("Inserting GO ancestor relationships...")
            GOAncestor.insert_all(vals)
            Logger.info(f"✓ Successfully inserted {len(vals)} ancestor relationships")
            message_dispatcher.notify_info_message(f"✓ Inserted {len(vals)} GO ancestors")
        else:
            Logger.warning("⚠ No ancestor relationships to insert")

        cls._log_table_states("AFTER ANCESTOR INSERTION")

        Logger.info("=" * 80)
        Logger.info("GO DATABASE CREATION COMPLETED SUCCESSFULLY")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ GO database completed!")

    @classmethod
    def _get_ancestors_query(cls, go):
        """
        Look for the go term ancestors and returns all go-go_ancestors relations in a list

        :returns: A list of dictionnaries in the following format: {'go': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in go.data:
            return vals
        for ancestor in go.data['ancestors']:
            if ancestor != go.go_id:
                val = {'go': go.id, 'ancestor': GO.get(
                    GO.go_id == ancestor).id}
                vals.append(val)
        return (vals)

    @classmethod
    def _deduplicate_ancestor_vals(cls, vals: list[dict], key1: str, key2: str) -> list[dict]:
        """Remove duplicate ancestor relationships"""
        Logger.info("Checking for duplicate ancestor relationships...")

        seen = set()
        unique_vals = []
        duplicates_count = 0

        for item in vals:
            key = (item[key1], item[key2])
            if key not in seen:
                seen.add(key)
                unique_vals.append(item)
            else:
                duplicates_count += 1

        if duplicates_count > 0:
            Logger.warning(f"⚠ Found {duplicates_count} DUPLICATE ancestor relationships!")
        else:
            Logger.info("✓ No duplicates found in ancestor relationships")

        return unique_vals

    @classmethod
    def _log_table_states(cls, stage: str):
        """Log the current state of GO-related tables"""
        try:
            Logger.info(f"--- TABLE STATES: {stage} ---")

            go_count = GO.select().count()
            Logger.info(f"  GO table: {go_count} records")

            try:
                ancestor_count = GOAncestor.select().count()
                Logger.info(f"  GOAncestor table: {ancestor_count} records")
            except Exception as e:
                Logger.info(f"  GOAncestor table: Not accessible ({type(e).__name__})")

            Logger.info("-" * 60)
        except Exception as e:
            Logger.warning(f"  Could not log table states: {e}")
