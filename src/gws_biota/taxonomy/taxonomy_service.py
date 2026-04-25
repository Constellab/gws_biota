

import csv
import os
import tempfile
from datetime import datetime, timezone

import pymysql
from gws_core import Logger, MessageDispatcher
from peewee import chunked
import uuid

from .._helper.ncbi import Taxonomy as NCBITaxonomyHelper
from ..base.base_service import BaseService
from ..db.biota_db_manager import BiotaDbManager
from .taxonomy import Taxonomy


class TaxonomyService(BaseService):

    @classmethod
    def create_taxonomy_db(cls, path, taxdump_files, message_dispatcher: MessageDispatcher = None):
        """
        Creates and fills the `taxonomy` database

        :param path: path to the folder that contain ncbi taxonomy dump files
        :type path: str
        :param taxdump_files: url that contains all data files names
        :type taxdump_files: tar.gz url
        :returns: None
        :rtype: None
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        ncbi_nodes = f"{taxdump_files}/nodes.dmp"
        ncbi_names = f"{taxdump_files}/names.dmp"
        ncbi_division = f"{taxdump_files}/division.dmp"

        Logger.info("Loading ncbi taxonomy file ...")
        message_dispatcher.notify_info_message("Parsing NCBI taxonomy files...")
        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(ncbi_names)
        dict_taxons = NCBITaxonomyHelper.get_all_taxonomy(
            dict_ncbi_names, ncbi_nodes, ncbi_division)

        taxa_count = len(dict_taxons)
        Logger.info(f"Saving {taxa_count} taxa ...")
        message_dispatcher.notify_info_message(f"Parsed {taxa_count} taxa — starting DB import...")

        # Discover ALL non-primary-key indexes at runtime, drop them before bulk insert.
        # Maintaining B-tree and FULLTEXT indexes during 2M+ row inserts multiplies write cost
        # by the number of indexes. Bulk-rebuilding them after is 10-50x faster.
        Logger.info("Inspecting indexes before bulk insert...")
        index_info = {}  # {key_name: {'columns': [col, ...], 'type': 'BTREE'|'FULLTEXT'}}
        try:
            for row in Taxonomy.execute_sql("SHOW INDEX FROM biota_taxonomy"):
                key_name = row[2]
                if key_name == 'PRIMARY':
                    continue
                if key_name not in index_info:
                    index_info[key_name] = {'columns': [], 'type': row[10]}
                index_info[key_name]['columns'].append((int(row[3]), row[4]))
            for info in index_info.values():
                info['columns'] = [col for _, col in sorted(info['columns'])]
        except Exception as e:
            Logger.warning(f"Could not inspect indexes (will proceed without dropping): {e}")

        Logger.info(f"Found {len(index_info)} indexes to drop: {list(index_info.keys())}")
        for key_name in index_info:
            try:
                Taxonomy.execute_sql(f"ALTER TABLE biota_taxonomy DROP INDEX `{key_name}`")
                Logger.info(f"  ✓ Dropped index: {key_name}")
            except Exception as e:
                Logger.warning(f"  Could not drop index {key_name}: {e}")

        # Disable session-level MariaDB checks — no uniqueness or FK constraints to validate here
        Taxonomy.execute_sql("SET SESSION unique_checks=0")
        Taxonomy.execute_sql("SET SESSION foreign_key_checks=0")
        # Use parallel sort threads for InnoDB FULLTEXT index rebuild (if supported)
        try:
            Taxonomy.execute_sql("SET SESSION innodb_ft_sort_pll_degree=4")
        except Exception:
            pass  # older MariaDB versions may not support this

        # Build all rows with UUIDs upfront, then sort by id before inserting.
        # UUIDs are random (uuid4) → inserting them unsorted causes random B-tree page splits in
        # InnoDB, which gets exponentially slower as the table grows beyond the buffer pool size.
        # Sorting by id makes inserts sequential → InnoDB streams pages → no random disk seeks.
        Logger.info("Preparing rows for bulk load...")
        message_dispatcher.notify_info_message("Preparing rows for bulk insert...")

        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        all_rows = []
        for data in dict_taxons.values():
            name = data.get('name', 'Unspecified')
            all_rows.append({
                'id': str(uuid.uuid4()),
                'tax_id': data['tax_id'],
                'name': name,
                'rank': data['rank'],
                'division': data['division'],
                'ancestor_tax_id': data['ancestor'],
                'ft_names': "TAX" + data['tax_id'] + ";" + name,
                'data': {},
            })
        # Sort by UUID → sequential B-tree insertions → constant-time inserts regardless of size
        all_rows.sort(key=lambda r: r['id'])
        Logger.info(f"✓ {len(all_rows)} rows prepared and sorted")

        # ── Strategy 1: LOAD DATA LOCAL INFILE (50–100x faster than row-by-row INSERT) ──────────
        # Write to a temp TSV file, then stream into MariaDB in a single server-side operation.
        # This bypasses Python/peewee overhead and avoids InnoDB buffer-pool saturation entirely.
        loaded = False
        tmpfile_path = None
        try:
            # Enable local_infile on the server (requires SUPER; ignore if not granted)
            try:
                Taxonomy.execute_sql("SET GLOBAL local_infile = 1")
            except Exception:
                pass

            with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.tsv', delete=False, newline='', encoding='utf-8') as tmpf:
                tmpfile_path = tmpf.name
                writer = csv.writer(tmpf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for row in all_rows:
                    writer.writerow([
                        row['id'],
                        now_str,              # created_at
                        now_str,              # last_modified_at
                        row['name'],
                        '{}',                 # data (JSON empty object)
                        row['ft_names'],
                        row['tax_id'],
                        row['rank'],
                        row['division'],
                        row['ancestor_tax_id'],
                    ])

            Logger.info(f"✓ Temp file written: {tmpfile_path}")
            message_dispatcher.notify_info_message("Data file ready — loading into database...")

            _mgr = BiotaDbManager.get_instance()
            _cfg = _mgr.get_config(_mgr.mode) if _mgr.mode else _mgr.get_prod_db_config()

            conn = pymysql.connect(
                host=_cfg.host,
                port=_cfg.port,
                user=_cfg.user,
                password=_cfg.password,
                database=_cfg.db_name,
                local_infile=True,
                charset='utf8mb4',
            )
            try:
                cursor = conn.cursor()
                # Escaped path (temp paths from tempfile are safe, but be explicit)
                safe_path = tmpfile_path.replace('\\', '\\\\').replace("'", "\\'")
                cursor.execute(f"""
                    LOAD DATA LOCAL INFILE '{safe_path}'
                    INTO TABLE biota_taxonomy
                    CHARACTER SET utf8mb4
                    FIELDS TERMINATED BY '\t'
                    OPTIONALLY ENCLOSED BY '"'
                    ESCAPED BY '\\\\'
                    LINES TERMINATED BY '\\n'
                    (id, created_at, last_modified_at, name, data, ft_names,
                     tax_id, rank, division, ancestor_tax_id)
                """)
                conn.commit()
                rows_loaded = cursor.rowcount
                loaded = True
                Logger.info(f"✓ LOAD DATA LOCAL INFILE completed: {rows_loaded} rows")
                message_dispatcher.notify_info_message(
                    f"Inserting taxa: {rows_loaded}/{taxa_count} (100%)")
            finally:
                conn.close()

        except Exception as e:
            Logger.warning(f"LOAD DATA LOCAL INFILE failed ({e}), falling back to batched INSERT...")

        finally:
            if tmpfile_path and os.path.exists(tmpfile_path):
                try:
                    os.unlink(tmpfile_path)
                except Exception:
                    pass

        # ── Strategy 2: fallback batched INSERT ──────────────────────────────────────────────────
        # Used only if LOAD DATA LOCAL INFILE is unavailable (e.g. server disables it).
        # Adds global InnoDB perf settings: skip fsync on every commit → reduces disk-write
        # stalls that cause the progressive slowdown observed beyond 1M rows.
        if not loaded:
            try:
                # Skip fsync after each commit (acceptable for a one-time rebuild)
                Taxonomy.execute_sql("SET GLOBAL innodb_flush_log_at_trx_commit = 0")
                Taxonomy.execute_sql("SET GLOBAL sync_binlog = 0")
            except Exception:
                pass

            db = Taxonomy.get_db()
            INSERT_BATCH = 50000   # larger batches → fewer round-trips
            total_inserted = 0
            # Wrap everything in a single transaction to eliminate per-batch commit overhead
            with db.atomic():
                for chunk in chunked(all_rows, INSERT_BATCH):
                    Taxonomy.insert_many(chunk).execute()
                    total_inserted += len(chunk)
                    if total_inserted % 500000 == 0 or total_inserted >= taxa_count:
                        msg = f"Inserting taxa: {total_inserted}/{taxa_count} ({100*total_inserted//taxa_count}%)"
                        Logger.info(f"  Progress: {msg}")
                        message_dispatcher.notify_info_message(msg)

            try:
                Taxonomy.execute_sql("SET GLOBAL innodb_flush_log_at_trx_commit = 1")
                Taxonomy.execute_sql("SET GLOBAL sync_binlog = 1")
            except Exception:
                pass

        all_rows = []

        Taxonomy.execute_sql("SET SESSION unique_checks=1")
        Taxonomy.execute_sql("SET SESSION foreign_key_checks=1")

        # Recreate all indexes in one bulk operation (MariaDB builds from sorted data = fast)
        Logger.info("Recreating all indexes after bulk insert...")
        message_dispatcher.notify_info_message("Rebuilding indexes (this may take several minutes)...")
        for key_name, info in index_info.items():
            cols = ','.join(info['columns'])
            try:
                if info['type'] == 'FULLTEXT':
                    Taxonomy.execute_sql(
                        f"CREATE FULLTEXT INDEX `{key_name}` ON biota_taxonomy({cols})")
                else:
                    Taxonomy.execute_sql(
                        f"CREATE INDEX `{key_name}` ON biota_taxonomy({cols})")
                Logger.info(f"  ✓ Recreated {info['type']} index: {key_name} ({cols})")
            except Exception as e:
                Logger.warning(f"  Could not recreate index {key_name}: {e}")

        Logger.info(f"✓ Successfully saved {taxa_count} taxa to database")
        message_dispatcher.notify_info_message(f"✓ {taxa_count} taxonomy entries saved successfully")
