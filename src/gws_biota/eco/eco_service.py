

from gws_core import Logger, MessageDispatcher

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from ..eco.eco import ECO, ECOAncestor


class ECOService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_eco_db(cls, path, eco_file, message_dispatcher: MessageDispatcher = None):
        """
        Creates and fills the `eco` database

        :param path: path of the :file:`eco.obo`
        :type path: str
        :param eco_file: file that contains data file name
        :type eco_file: file
        :returns: None
        :rtype: None
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("STARTING ECO DATABASE CREATION")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("Starting ECO database creation...")

        cls._log_table_states("BEFORE CREATION")

        Logger.info("-" * 80)
        Logger.info("STEP 1: Parsing and inserting ECO terms")
        Logger.info("-" * 80)

        data_dir, corrected_file_name = OntoHelper.correction_of_eco_file(
            path, eco_file)
        Logger.info(f"tuple : {data_dir}, {corrected_file_name}")

        onto_eco = OntoHelper.create_ontology_from_file(
            data_dir, corrected_file_name)

        list_eco = OntoHelper.parse_eco_terms_from_ontoloy(onto_eco)
        Logger.info(f"Parsed {len(list_eco)} ECO terms from file")

        ecos = [ECO(data=dict_) for dict_ in list_eco]
        for eco in ecos:
            eco.set_eco_id(eco.data["id"])
            eco.set_name(eco.data["name"])
            ft_names = [eco.data["name"], "ECO" +
                        eco.eco_id.replace("ECO:", "")]
            eco.ft_names = cls.format_ft_names(ft_names)
            del eco.data["id"]

        Logger.info(f"Creating {len(ecos)} ECO records...")
        ECO.create_all(ecos)
        Logger.info(f"✓ Successfully created {len(ecos)} ECO records")
        message_dispatcher.notify_info_message(f"✓ Created {len(ecos)} ECO records")

        cls._log_table_states("AFTER ECO INSERTION")

        Logger.info("-" * 80)
        Logger.info("STEP 2: Inserting ECO ancestor relationships")
        Logger.info("-" * 80)

        vals = []
        for eco in ecos:
            val = cls._get_ancestors_query(eco)
            for v in val:
                vals.append(v)

        Logger.info(f"Generated {len(vals)} ancestor relationship records")

        # Deduplicate before insertion
        vals = cls._deduplicate_ancestor_vals(vals, 'eco', 'ancestor')
        Logger.info(f"After deduplication: {len(vals)} records to insert")

        if vals:
            Logger.info("Inserting ECO ancestor relationships...")
            ECOAncestor.insert_all(vals)
            Logger.info(f"✓ Successfully inserted {len(vals)} ancestor relationships")
            message_dispatcher.notify_info_message(f"✓ Inserted {len(vals)} ECO ancestors")
        else:
            Logger.warning("⚠ No ancestor relationships to insert")

        cls._log_table_states("AFTER ANCESTOR INSERTION")

        Logger.info("=" * 80)
        Logger.info("ECO DATABASE CREATION COMPLETED SUCCESSFULLY")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ ECO database completed!")

    @classmethod
    def _get_ancestors_query(cls, eco):
        """
        Look for the eco term ancestors and returns all eco-eco_ancetors relations in a list

        :returns: a list of dictionnaries inf the following format: {'eco': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in eco.data:
            return vals
        for ancestor in eco.data['ancestors']:
            if ancestor != eco.eco_id:
                val = {'eco': eco.id, 'ancestor': ECO.get(
                    ECO.eco_id == ancestor).id}
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
        """Log the current state of ECO-related tables"""
        try:
            Logger.info(f"--- TABLE STATES: {stage} ---")

            eco_count = ECO.select().count()
            Logger.info(f"  ECO table: {eco_count} records")

            try:
                ancestor_count = ECOAncestor.select().count()
                Logger.info(f"  ECOAncestor table: {ancestor_count} records")
            except Exception as e:
                Logger.info(f"  ECOAncestor table: Not accessible ({type(e).__name__})")

            Logger.info("-" * 60)
        except Exception as e:
            Logger.warning(f"  Could not log table states: {e}")
