

from gws_core import Logger, MessageDispatcher

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from .sbo import SBO, SBOAncestor


class SBOService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_sbo_db(cls, path, sbo_file, message_dispatcher: MessageDispatcher = None):
        """
        Creates and fills the `sbo` database

        :param biodata_dir: path to the folder that contain the :file:`sbo.obo` file
        :type biodata_dir: str
        :param sbo_file: file that contains data file name
        :type sbo_file: file
        :returns: None
        :rtype: None
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("STARTING SBO DATABASE CREATION")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("Starting SBO database creation...")

        cls._log_table_states("BEFORE CREATION")

        Logger.info("-" * 80)
        Logger.info("STEP 1: Parsing and inserting SBO terms")
        Logger.info("-" * 80)

        data_dir, corrected_file_name = OntoHelper.correction_of_sbo_file(
            path, sbo_file)
        ontology = OntoHelper.create_ontology_from_file(
            data_dir, corrected_file_name)
        list_sbo = OntoHelper.parse_sbo_terms_from_ontology(ontology)
        Logger.info(f"Parsed {len(list_sbo)} SBO terms from file")

        sbos = [SBO(data=dict_) for dict_ in list_sbo]
        for sbo in sbos:
            sbo.set_sbo_id(sbo.data["id"])
            sbo.set_name(sbo.data["name"])
            ft_names = [sbo.data["name"], sbo.data["id"].replace(":", "")]
            sbo.ft_names = cls.format_ft_names(ft_names)
            del sbo.data["id"]

        Logger.info(f"Creating {len(sbos)} SBO records...")
        SBO.create_all(sbos)
        Logger.info(f"✓ Successfully created {len(sbos)} SBO records")
        message_dispatcher.notify_info_message(f"✓ Created {len(sbos)} SBO records")

        cls._log_table_states("AFTER SBO INSERTION")

        Logger.info("-" * 80)
        Logger.info("STEP 2: Inserting SBO ancestor relationships")
        Logger.info("-" * 80)

        vals = []
        for sbo in sbos:
            val = cls._get_ancestors_query(sbo)
            for v in val:
                vals.append(v)

        Logger.info(f"Generated {len(vals)} ancestor relationship records")

        # Deduplicate before insertion
        vals = cls._deduplicate_ancestor_vals(vals, 'sbo', 'ancestor')
        Logger.info(f"After deduplication: {len(vals)} records to insert")

        if vals:
            Logger.info("Inserting SBO ancestor relationships...")
            SBOAncestor.insert_all(vals)
            Logger.info(f"✓ Successfully inserted {len(vals)} ancestor relationships")
            message_dispatcher.notify_info_message(f"✓ Inserted {len(vals)} SBO ancestors")
        else:
            Logger.warning("⚠ No ancestor relationships to insert")

        cls._log_table_states("AFTER ANCESTOR INSERTION")

        Logger.info("=" * 80)
        Logger.info("SBO DATABASE CREATION COMPLETED SUCCESSFULLY")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ SBO database completed!")

    @classmethod
    def _get_ancestors_query(cls, sbo):
        """
        Look for the sbo term ancestors and returns all sbo-sbo_ancestors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'sbo': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in sbo.data:
            return vals
        for ancestor in sbo.data['ancestors']:
            if (ancestor != sbo.sbo_id):
                val = {'sbo': sbo.id, 'ancestor': SBO.get(
                    SBO.sbo_id == ancestor).id}
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
        """Log the current state of SBO-related tables"""
        try:
            Logger.info(f"--- TABLE STATES: {stage} ---")

            sbo_count = SBO.select().count()
            Logger.info(f"  SBO table: {sbo_count} records")

            try:
                ancestor_count = SBOAncestor.select().count()
                Logger.info(f"  SBOAncestor table: {ancestor_count} records")
            except Exception as e:
                Logger.info(f"  SBOAncestor table: Not accessible ({type(e).__name__})")

            Logger.info("-" * 60)
        except Exception as e:
            Logger.warning(f"  Could not log table states: {e}")
