

import math

from gws_core import Logger, MessageDispatcher
from peewee import chunked

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.chebi import Chebi as ChebiHelper
from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from ..compound.compound import Compound, CompoundAncestor


class CompoundService(BaseService):

    @staticmethod
    def _to_float(val):
        try:
            val = float(val)
        except Exception as _:
            return None
        if math.isnan(val):
            val = None
        return val

    @classmethod
    @BiotaDbManager.transaction()
    def create_compound_db(cls, path, compound_file, message_dispatcher: MessageDispatcher = None) -> None:
        """
        Creates and fills the `chebi_ontology` database

        :type compound_file_path: file
        :param compound_file_path: path of chebi data
        :returns: None
        :rtype: None
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("STARTING COMPOUND DATABASE CREATION")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("Starting Compound database creation...")

        cls._log_table_states("BEFORE CREATION")

        Logger.info("-" * 80)
        Logger.info("STEP 1: Parsing and inserting compounds")
        Logger.info("-" * 80)

        data_dir, corrected_file_name = ChebiHelper.correction_of_chebi_file(
            path, compound_file)
        onto_chebi = OntoHelper.create_ontology_from_file(
            data_dir, corrected_file_name)

        list_chebi = OntoHelper.parse_chebi_from_ontology(onto_chebi)

        comp_count = len(list_chebi)
        Logger.info(f"Saving {comp_count} compounds ...")
        compounds = [Compound(data=data) for data in list_chebi]
        for compound_chunk in chunked(compounds, cls.BATCH_SIZE):
            for comp in compound_chunk:
                comp.set_name(comp.data["name"])
                comp.chebi_id = comp.data["id"]
                comp.formula = comp.data["formula"]
                comp.inchi = comp.data["inchi"]
                comp.inchikey = comp.data["inchikey"]
                comp.smiles = comp.data["smiles"]
                if comp.data["mass"] is not None:
                    comp.mass = cls._to_float(comp.data["mass"])
                if comp.data["monoisotopic_mass"] is not None:
                    comp.monoisotopic_mass = cls._to_float(
                        comp.data["monoisotopic_mass"])
                if comp.data["charge"] is not None:
                    comp.charge = cls._to_float(comp.data["charge"])
                comp.chebi_star = comp.data["subsets"]
                if "kegg" in comp.data["xref"]:
                    comp.kegg_id = comp.data["xref"]["kegg"]
                    del comp.data["xref"]["kegg"]
                if "metacyc" in comp.data["xref"]:
                    comp.metacyc_id = comp.data["xref"]["metacyc"]
                    del comp.data["xref"]["metacyc"]

                all_ids = [comp.chebi_id, *comp.alt_chebi_ids]
                if comp.kegg_id is not None:
                    all_ids.append(comp.kegg_id)
                all_ids_trimed = [elt.replace(":", "") for elt in all_ids]
                ft_names = [comp.data["name"], *all_ids_trimed]
                comp.ft_names = cls.format_ft_names(ft_names)

                del comp.data["id"]
                del comp.data["inchi"]
                del comp.data["formula"]
                del comp.data["inchikey"]
                del comp.data["smiles"]
                del comp.data["mass"]
                del comp.data["monoisotopic_mass"]
                del comp.data["charge"]
                del comp.data["subsets"]
            Compound.create_all(compound_chunk)

        # save ancestors
        Logger.info("-" * 80)
        Logger.info("STEP 2: Inserting compound ancestor relationships")
        Logger.info("-" * 80)

        vals = []
        for compound in compounds:
            val = cls._get_ancestors_query(compound)
            for v in val:
                vals.append(v)

        Logger.info(f"Generated {len(vals)} ancestor relationship records")

        # Deduplicate before insertion
        vals = cls._deduplicate_ancestor_vals(vals, 'compound', 'ancestor')
        Logger.info(f"After deduplication: {len(vals)} records to insert")

        if vals:
            Logger.info("Inserting compound ancestor relationships...")
            CompoundAncestor.insert_all(vals)
            Logger.info(f"✓ Successfully inserted {len(vals)} ancestor relationships")
            message_dispatcher.notify_info_message(f"✓ Inserted {len(vals)} compound ancestors")
        else:
            Logger.warning("⚠ No ancestor relationships to insert")

        Logger.info("=" * 80)
        Logger.info("COMPOUND DATABASE CREATION COMPLETED SUCCESSFULLY")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ Compound database completed!")

    @classmethod
    def _get_ancestors_query(cls, compound):
        """
        Look for the compound term ancestors and returns all ancetors relations in a list

        :returns: a list of dictionnaries inf the following format: {'compound': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in compound.data:
            return vals
        for ancestor in compound.data['ancestors']:
            if ancestor != compound.chebi_id:
                val = {'compound': compound.id, 'ancestor': Compound.get(
                    Compound.chebi_id == ancestor).id}
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
        """Log the current state of Compound-related tables"""
        try:
            Logger.info(f"--- TABLE STATES: {stage} ---")

            compound_count = Compound.select().count()
            Logger.info(f"  Compound table: {compound_count} records")

            try:
                ancestor_count = CompoundAncestor.select().count()
                Logger.info(f"  CompoundAncestor table: {ancestor_count} records")
            except Exception as e:
                Logger.info(f"  CompoundAncestor table: Not accessible ({type(e).__name__})")

            Logger.info("-" * 60)
        except Exception as e:
            Logger.warning(f"  Could not log table states: {e}")
