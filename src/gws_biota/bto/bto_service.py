from gws_core import Logger, MessageDispatcher

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from .bto import BTO, BTOAncestor


class BTOService(BaseService):
    @classmethod
    @BiotaDbManager.transaction()
    def create_bto_db(cls, destination_dir, bto_file_path: str, message_dispatcher: MessageDispatcher = None) -> None:
        """
        Creates and fills the `bto` database

        :param bto_file: path of bto.owl file
        :type bto_file: file
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("STARTING BTO DATABASE CREATION")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("Starting BTO database creation...")

        cls._log_table_states("BEFORE CREATION")

        Logger.info("-" * 80)
        Logger.info("STEP 1: Parsing and inserting BTO terms")
        Logger.info("-" * 80)

        # convert to obo if required
        ontology = OntoHelper.create_ontology_from_file(destination_dir, bto_file_path)
        list_bto = OntoHelper.parse_bto_from_ontology(ontology)
        Logger.info(f"Parsed {len(list_bto)} BTO terms from file")

        btos: list[BTO] = [BTO(data=dict_) for dict_ in list_bto]
        for bto in btos:
            bto.set_bto_id(bto.data["id"])
            bto.set_name(bto.data["name"])
            ft_names = [bto.data["name"], "BTO" + bto.bto_id.replace("BTO:", "")]
            bto.ft_names = cls.format_ft_names(ft_names)
            del bto.data["id"]

        Logger.info(f"Creating {len(btos)} BTO records...")
        BTO.create_all(btos)
        Logger.info(f"✓ Successfully created {len(btos)} BTO records")
        message_dispatcher.notify_info_message(f"✓ Created {len(btos)} BTO records")

        cls._log_table_states("AFTER BTO INSERTION")

        Logger.info("-" * 80)
        Logger.info("STEP 2: Inserting BTO ancestor relationships")
        Logger.info("-" * 80)

        vals = []
        for bto in btos:
            val = cls._get_ancestors_query(bto)
            for v in val:
                vals.append(v)

        Logger.info(f"Generated {len(vals)} ancestor relationship records")

        # Deduplicate before insertion
        vals = cls._deduplicate_ancestor_vals(vals, 'bto', 'ancestor')
        Logger.info(f"After deduplication: {len(vals)} records to insert")

        if vals:
            Logger.info("Inserting BTO ancestor relationships...")
            BTOAncestor.insert_all(vals)
            Logger.info(f"✓ Successfully inserted {len(vals)} ancestor relationships")
            message_dispatcher.notify_info_message(f"✓ Inserted {len(vals)} ancestor relationships")
        else:
            Logger.warning("⚠ No ancestor relationships to insert")
            message_dispatcher.notify_info_message("⚠ No ancestor relationships to insert")

        cls._log_table_states("AFTER ANCESTOR INSERTION")

        Logger.info("=" * 80)
        Logger.info("BTO DATABASE CREATION COMPLETED SUCCESSFULLY")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ BTO database completed!")

    @classmethod
    def _get_ancestors_query(cls, bto: BTO) -> list[dict]:
        """
        Look for the bto term ancestors and returns all bto-bto_ancetors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'bto': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals: list[dict] = []
        if "ancestors" not in bto.data:
            return vals
        for ancestor in bto.data["ancestors"]:
            if ancestor != bto.bto_id:
                ancestors: list[BTO] = list(BTO.select(BTO.id).where(BTO.bto_id == ancestor))
                if len(ancestors) > 0:
                    val = {"bto": bto.id, "ancestor": ancestors[0].id}
                    vals.append(val)
        return vals

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
        """Log the current state of BTO-related tables"""
        try:
            Logger.info(f"--- TABLE STATES: {stage} ---")

            bto_count = BTO.select().count()
            Logger.info(f"  BTO table: {bto_count} records")

            try:
                ancestor_count = BTOAncestor.select().count()
                Logger.info(f"  BTOAncestor table: {ancestor_count} records")
            except Exception as e:
                Logger.info(f"  BTOAncestor table: Not accessible ({type(e).__name__})")

            Logger.info("-" * 60)
        except Exception as e:
            Logger.warning(f"  Could not log table states: {e}")
