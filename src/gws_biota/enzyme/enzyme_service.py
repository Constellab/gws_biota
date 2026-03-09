from gws_core import Logger, MessageDispatcher, Settings
from peewee import chunked

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.bkms import BKMS
from .._helper.brenda import Brenda
from ..base.base_service import BaseService
from ..bto.bto import BTO
from ..taxonomy.taxonomy import Taxonomy
from .deprecated_enzyme import DeprecatedEnzyme
from .enzyme import Enzyme, EnzymeBTO
from .enzyme_class import EnzymeClass
from .enzyme_ortholog import EnzymeOrtholog
from .enzyme_pathway import EnzymePathway


class EnzymeService(BaseService):
    @classmethod
    def create_enzyme_db(
        cls, brenda_file, bkms_file, expasy_file, taxonomy_file, bto_file, compound_file, message_dispatcher=None
    ):
        """
        Creates and fills the `enzyme` database
        Transaction is delayed until after parsing to avoid MariaDB timeout during long BRENDA parsing
        :param: enzymes files
        :type files: file
        :param message_dispatcher: Message dispatcher for UI logging
        :type message_dispatcher: MessageDispatcher
        :returns: None
        :rtype: None
        """

        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        base_biodata_dir = Settings.get_instance().get_variable("gws_biota", "biodata_dir")

        # Force UTF-8 encoding for ChEBI file parsing
        # This prevents chardet from misdetecting chebi.obo as cp1252
        # which causes UnicodeDecodeError in pronto.Ontology()
        Logger.info("Patching pronto to force UTF-8 encoding for ChEBI file...")
        import pronto.ontology as pronto_ontology
        import pronto.utils.io as pronto_io

        original_decompress = pronto_io.decompress

        def _decompress_utf8(reader, path=None, encoding=None):
            return original_decompress(reader, path, encoding="utf-8")

        pronto_io.decompress = _decompress_utf8
        pronto_ontology.decompress = original_decompress

        try:
            # ==================================================================
            # PHASE 1: Quick DB operations (enzyme classes)
            # ==================================================================
            message_dispatcher.notify_info_message("Loading enzyme classes...")
            Logger.info("Loading enzyme classes...")
            EnzymeClass.create_enzyme_class_db(base_biodata_dir, expasy_file)

            # CRITICAL: Close DB connection to prevent timeout during long parsing
            message_dispatcher.notify_info_message("✓ Enzyme classes loaded")
            Logger.info("Closing and clearing database connection before long parsing phase...")
            # Force close all connections to prevent timeout issues
            try:
                if not BiotaDbManager.db.is_closed():
                    BiotaDbManager.db.close()
                # Clear connection pool to force fresh connection later
                if hasattr(BiotaDbManager.db, '_state'):
                    BiotaDbManager.db._state.reset()
            except Exception as e:
                Logger.warning(f"Error closing connection: {e}")
                pass

            # ==================================================================
            # PHASE 2: PARSING (NO DB CONNECTION - AVOID TIMEOUT)
            # ==================================================================
            message_dispatcher.notify_info_message("=" * 80)
            message_dispatcher.notify_info_message("PARSING BRENDA FILE (this may take 30-60 minutes)...")
            message_dispatcher.notify_info_message("=" * 80)
            Logger.info("Starting BRENDA parsing...")
            brenda = Brenda(
                brenda_file=brenda_file,
                taxonomy_dir=taxonomy_file,
                bto_file=bto_file,
                chebi_file=compound_file,
            )

            list_of_enzymes, list_deprecated_ec = brenda.parse_all_enzyme_to_dict()
            message_dispatcher.notify_info_message("=" * 80)
            message_dispatcher.notify_info_message(f"✓ BRENDA PARSING COMPLETED - {len(list_of_enzymes)} enzymes parsed")
            message_dispatcher.notify_info_message("=" * 80)
            Logger.info(f"BRENDA parsing completed - {len(list_of_enzymes)} enzymes")

            # ==================================================================
            # PHASE 3: PREPARE DATA STRUCTURES (NO DB OPERATIONS)
            # ==================================================================
            message_dispatcher.notify_info_message("Preparing data structures for database insertion...")
            Logger.info("Preparing data structures for database insertion...")

            # Prepare EnzymePathway objects
            pathways = {}
            for d in list_of_enzymes:
                ec = d["ec"]
                if ec not in pathways:
                    pathways[ec] = EnzymePathway(ec_number=ec)
            Logger.info(f"  Prepared {len(pathways)} enzyme pathways")

            # Prepare EnzymeOrtholog objects
            enzos = {}
            for d in list_of_enzymes:
                ec = d["ec"]
                if ec not in enzos:
                    rn = d["RN"]
                    sn = d.get("SN", [])
                    sy = [k.get("data", "") for k in d.get("SY", [])]
                    ft_names = ["EC" + ec.replace(".", ""), *rn, *sn, *sy]
                    enzos[ec] = EnzymeOrtholog(
                        ec_number=ec,
                        data={"RN": rn, "SN": sn, "SY": sy},
                        ft_names=cls.format_ft_names(ft_names),
                    )
                    enzos[ec].set_name(d["RN"][0])
                    enzos[ec].pathway = pathways[ec]
            Logger.info(f"  Prepared {len(enzos)} enzyme orthologs")

            # Prepare Enzyme objects
            enzymes = []
            for d in list_of_enzymes:
                ec = d["ec"]
                rn = d["RN"]
                sn = d.get("SN", [])
                sy = [k.get("data", "") for k in d.get("SY", [])]
                organism = d.get("organism")
                enz = Enzyme(
                    ec_number=ec,
                    uniprot_id=d["uniprot"],
                    data=d,
                    ft_names=";".join(["EC" + ec.replace(".", ""), *rn, *sn, *sy, organism]),
                )
                enz.set_name(d["RN"][0])
                enzymes.append(enz)
            Logger.info(f"  Prepared {len(enzymes)} enzymes")

            # Prepare deprecated enzymes - flatten and resolve nested relations
            all_old_ecs = [elt["old_ec"] for elt in list_deprecated_ec]
            list_deprecated_ec = {elt["old_ec"]: elt for elt in list_deprecated_ec}
            is_nested = True
            while is_nested:
                is_nested = False
                for dep_ec in list_deprecated_ec.values():
                    new_list = []
                    for new_ec in dep_ec["new_ec"]:
                        if new_ec in all_old_ecs:
                            is_nested = True
                            if new_ec == dep_ec["old_ec"]:
                                dep_ec["new_ec"].remove(new_ec)
                            if new_ec in list_deprecated_ec:
                                next_dep_ec = list_deprecated_ec[new_ec]
                                new_list.extend(next_dep_ec["new_ec"])
                                new_list = list(set(new_list))
                                for key, val in next_dep_ec["data"].items():
                                    dep_ec["data"][key] += ";" + val
                            else:
                                dep_ec["data"]["reason"] += f"; {new_ec} probably deleted"
                        else:
                            new_list.append(new_ec)
                            new_list = list(set(new_list))
                    dep_ec["new_ec"] = new_list

            deprecated_enzymes = []
            for old_ec, elt in list_deprecated_ec.items():
                if len(elt["new_ec"]) == 0:
                    elt["new_ec"] = [None]
                for new_ec in elt["new_ec"]:
                    t_enz = DeprecatedEnzyme(
                        ec_number=old_ec,
                        new_ec_number=new_ec,
                        data=elt["data"],
                    )
                    deprecated_enzymes.append(t_enz)
            Logger.info(f"  Prepared {len(deprecated_enzymes)} deprecated enzymes")

            # Parse BKMS data if available (optional)
            list_of_bkms = None
            if bkms_file:
                Logger.info("Parsing BKMS file...")
                list_of_bkms = BKMS.parse_csv_from_file(base_biodata_dir, bkms_file)
                Logger.info(f"  Parsed {len(list_of_bkms)} BKMS entries")
            else:
                Logger.info("  BKMS file not available - will skip pathway enrichment")

            message_dispatcher.notify_info_message(
                f"✓ Data preparation complete: {len(pathways)} pathways, "
                f"{len(enzos)} orthologs, {len(enzymes)} enzymes, "
                f"{len(deprecated_enzymes)} deprecated"
            )

            # ==================================================================
            # PHASE 4: SAVE TO DATABASE (NO EXPLICIT TRANSACTIONS)
            # ==================================================================
            # Note: create_all(), update_all(), and insert_all() already use
            # db.atomic() internally for transaction management. Adding explicit
            # transactions here causes nested transactions that timeout on MariaDB.
            # ==================================================================
            message_dispatcher.notify_info_message("=" * 80)
            message_dispatcher.notify_info_message("SAVING ALL DATA TO DATABASE...")
            message_dispatcher.notify_info_message("=" * 80)

            # CRITICAL: Ensure fresh database connection with ping test
            Logger.info("Reconnecting to database with fresh connection...")
            message_dispatcher.notify_info_message("Reconnecting to database...")

            # Force close and reconnect
            try:
                if not BiotaDbManager.db.is_closed():
                    BiotaDbManager.db.close()
            except:
                pass

            # Open new connection
            BiotaDbManager.db.connect()

            # Test connection with ping
            try:
                BiotaDbManager.db.execute_sql('SELECT 1')
                Logger.info("✓ Database connection verified")
                message_dispatcher.notify_info_message("✓ Database connection ready")
            except Exception as e:
                Logger.error(f"Connection test failed: {e}")
                # Try one more time
                BiotaDbManager.db.close()
                BiotaDbManager.db.connect()
                BiotaDbManager.db.execute_sql('SELECT 1')
                Logger.info("✓ Database connection verified (retry)")

            # Save core enzyme data
            message_dispatcher.notify_info_message("Saving enzyme pathways...")
            EnzymePathway.create_all(list(pathways.values()))
            message_dispatcher.notify_info_message(f"✓ Saved {len(pathways)} enzyme pathways")

            message_dispatcher.notify_info_message("Saving enzyme orthologs...")
            EnzymeOrtholog.create_all(list(enzos.values()))
            message_dispatcher.notify_info_message(f"✓ Saved {len(enzos)} enzyme orthologs")

            # Save enzymes in SMALL chunks to avoid MariaDB timeout
            # Each chunk = 1 transaction. 10K was still too big, use 1K instead.
            # MariaDB timeouts after ~60 sec of transaction, so keep each transaction < 5 sec
            # Force fresh DB connection before starting saves
            db = Enzyme.get_db()
            db.close()
            db.connect()
            message_dispatcher.notify_info_message("Reconnected to database for saves")

            message_dispatcher.notify_info_message(f"Saving {len(enzymes)} enzymes in small chunks...")
            chunk_size = 1000  # Small chunks to keep each transaction under 5 seconds
            num_chunks = (len(enzymes) + chunk_size - 1) // chunk_size

            saved_count = 0
            for chunk in chunked(enzymes, chunk_size):
                chunk_list = list(chunk)

                # Ping DB before each chunk to keep connection alive
                try:
                    db.execute_sql('SELECT 1')
                except Exception:
                    # Connection lost, reconnect
                    db.close()
                    db.connect()
                    message_dispatcher.notify_info_message("  ⚠ Reconnected to database (connection was lost)")

                # batch_size=100: smaller INSERTs to avoid "MySQL server has gone away"
                Enzyme.create_all(chunk_list, batch_size=100, use_transaction=False)
                saved_count += len(chunk_list)
                if saved_count % (chunk_size * 10) == 0:  # Log every 10 chunks (10K enzymes)
                    message_dispatcher.notify_info_message(f"  Progress: {saved_count}/{len(enzymes)} enzymes saved...")

            message_dispatcher.notify_info_message(f"✓ Saved {len(enzymes)} enzymes")

            if deprecated_enzymes:
                message_dispatcher.notify_info_message("Saving deprecated enzymes...")
                DeprecatedEnzyme.create_all(deprecated_enzymes)
                message_dispatcher.notify_info_message(f"✓ Saved {len(deprecated_enzymes)} deprecated enzymes")

            # Update taxonomy in chunks to avoid single long transaction
            message_dispatcher.notify_info_message(f"Updating taxonomy for {len(enzymes)} enzymes in chunks...")
            updated_count = 0
            for chunk in chunked(enzymes, chunk_size):
                chunk_list = list(chunk)
                cls.__update_taxonomy(chunk_list)
                updated_count += len(chunk_list)
                if updated_count % (chunk_size * 10) == 0:  # Log every 10 chunks (10K enzymes)
                    message_dispatcher.notify_info_message(f"  Progress: {updated_count}/{len(enzymes)} taxonomy updated...")
            message_dispatcher.notify_info_message("✓ Taxonomy updated")

            # Update BTO in chunks to avoid single long transaction
            message_dispatcher.notify_info_message(f"Updating BTO for {len(enzymes)} enzymes in chunks...")
            updated_count = 0
            for chunk in chunked(enzymes, chunk_size):
                chunk_list = list(chunk)
                cls.__update_bto(chunk_list)
                updated_count += len(chunk_list)
                if updated_count % (chunk_size * 10) == 0:  # Log every 10 chunks (10K enzymes)
                    message_dispatcher.notify_info_message(f"  Progress: {updated_count}/{len(enzymes)} BTO updated...")
            message_dispatcher.notify_info_message("✓ BTO updated")

            if list_of_bkms:
                message_dispatcher.notify_info_message("Updating enzyme pathways with BKMS data...")
                cls.__update_pathway_from_bkms(list_of_bkms)
                message_dispatcher.notify_info_message("✓ BKMS data integrated")
            else:
                message_dispatcher.notify_info_message("⚠ BKMS pathway enrichment skipped (no data)")

            message_dispatcher.notify_info_message("=" * 80)
            message_dispatcher.notify_info_message("✓ ALL ENZYME DATA SAVED SUCCESSFULLY")
            message_dispatcher.notify_info_message("=" * 80)

        finally:
            # Restore original pronto decompress function
            Logger.info("Restoring original pronto decompress function...")
            pronto_io.decompress = original_decompress
            pronto_ontology.decompress = original_decompress

    # -- U --

    @classmethod
    def __update_taxonomy(cls, enzymes):
        for enz in enzymes:
            cls.__set_taxonomy_data(enz)
        fields = ["tax_" + t for t in Taxonomy.get_tax_tree()]
        Enzyme.update_all(enzymes, fields=["tax_id", *fields])

    @classmethod
    def __update_bto(cls, enzymes):
        vals = []
        for enz in enzymes:
            vals.extend(cls.__create_bto_values(enz))
        EnzymeBTO.insert_all(vals)

    @classmethod
    def __set_taxonomy_data(cls, enzyme):
        """
        See if there is any information about the enzyme taxonomy and if so, connects
        the enzyme and its taxonomy by adding the related tax_id from the taxonomy
        table to the taxonomy property of the enzyme
        """

        if "taxonomy" in enzyme.data:
            try:
                enzyme.tax_id = str(enzyme.data["taxonomy"])
                tax = Taxonomy.get(Taxonomy.tax_id == enzyme.tax_id)
                setattr(enzyme, "tax_" + tax.rank, tax.tax_id)
                for t in tax.ancestors:
                    if t.rank in Taxonomy.get_tax_tree():
                        setattr(enzyme, "tax_" + t.rank, t.tax_id)
                del enzyme.data["taxonomy"]
            except Exception as _:
                pass

    @classmethod
    def __create_bto_values(cls, enzyme):
        """
        See if there is any information about the enzyme tissue locations and if so,
        connects the enzyme and tissues by adding an enzyme-tissues relation
        in the enzyme_btos table
        """

        n = len(enzyme.get_params("ST"))
        bto_ids = []
        for i in range(0, n):
            bto_ids.append(enzyme.get_params("ST")[i].get("bto"))
        Q = BTO.select().where(BTO.bto_id << bto_ids)

        vals = []
        for bto in Q:
            vals.append({"bto": bto.id, "enzyme": enzyme.id})
        return vals

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the biochemical reaction and if so,
        connects the enzyme and biochemical reaction by adding an enzyme-bkms relation
        in the biota_enzyme_pathway
        """

        pathways = {}
        dbs = ["brenda", "kegg", "metacyc"]
        for bkms in list_of_bkms:
            ec_number = bkms["ec_number"]
            Q = EnzymePathway.select().where(EnzymePathway.ec_number == ec_number)
            for pathway in Q:
                for k in dbs:
                    if bkms.get(k + "_pathway_name"):
                        pwy_id = bkms.get(k + "_pathway_id", "")
                        pwy_name = bkms[k + "_pathway_name"]
                        pathway.data[k] = {"id": pwy_id, "name": pwy_name}

                pathways[pathway.ec_number] = pathway

        EnzymePathway.update_all(pathways.values(), fields=["data"])
