


import os
import subprocess
from gws_core import Logger, MessageDispatcher

from gws_biota.base.base import Base

from .biota_db_manager import BiotaDbManager


class DbService:

    @staticmethod
    def ensure_pigz_installed() -> None:
        """
        Ensures that pigz is installed on the system.
        pigz is required by gws_core's FileDownloader to decompress .tar.gz files.
        If not already installed, installs it automatically via apt-get.
        """
        # Check if pigz is already available
        result = subprocess.run(["which", "pigz"], capture_output=True)
        if result.returncode == 0:
            Logger.info("pigz already installed")
            return

        Logger.info("pigz not found — installing automatically...")
        try:
            subprocess.run(
                ["apt-get", "install", "-y", "pigz"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            Logger.info("✓ pigz installed successfully")
        except Exception as e:
            Logger.warning(f"⚠ Could not install pigz automatically: {e}. Falling back to Python's tarfile module.")

    @classmethod
    def clean_python_cache(cls, message_dispatcher: MessageDispatcher = None) -> None:
        """
        Clean Python cache files to ensure fresh state and avoid conflicts/duplicates.
        This should be called at the start of each database creation task.

        :param message_dispatcher: Optional message dispatcher for UI feedback
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("=" * 80)
        Logger.info("CLEANING PYTHON CACHE")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("🧹 Cleaning Python cache...")

        # Clean gws_biota brick cache
        biota_path = "/lab/user/bricks/gws_biota"
        if os.path.exists(biota_path):
            Logger.info(f"Cleaning cache in {biota_path}...")
            subprocess.run(
                ["find", biota_path, "-type", "d", "-name", "__pycache__", "-exec", "rm", "-rf", "{}", "+"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            subprocess.run(
                ["find", biota_path, "-name", "*.pyc", "-delete"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            Logger.info("✓ gws_biota cache cleaned")

        # Clean brendapy cache if it exists (for enzyme database)
        brendapy_path = "/lab/.sys/lib/brendapy"
        if os.path.exists(brendapy_path):
            Logger.info(f"Cleaning cache in {brendapy_path}...")
            subprocess.run(
                ["find", brendapy_path, "-type", "d", "-name", "__pycache__", "-exec", "rm", "-rf", "{}", "+"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            subprocess.run(
                ["find", brendapy_path, "-name", "*.pyc", "-delete"],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
            )
            Logger.info("✓ brendapy cache cleaned")

        Logger.info("=" * 80)
        Logger.info("CACHE CLEANING COMPLETED")
        Logger.info("=" * 80)
        message_dispatcher.notify_info_message("✓ Python cache cleaned - starting with fresh state")

    @classmethod
    def drop_biota_tables(cls, biota_models: list[type[Base]], message_dispatcher: MessageDispatcher = None) -> None:
        """
        Drop biota tables with detailed logging

        :param biota_models: List of model classes to drop
        :param message_dispatcher: Optional message dispatcher for UI feedback
        """
        Logger.info("=" * 80)
        Logger.info("DROPPING BIOTA TABLES")
        Logger.info("=" * 80)

        BiotaDbManager._DEACTIVATE_PROTECTION_ = True

        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        Logger.info("Disabling foreign key checks...")
        BiotaDbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        Logger.info("✓ Foreign key checks disabled")

        for idx, biota_model in enumerate(biota_models, 1):
            table_name = biota_model.__name__
            Logger.info(f"[{idx}/{len(biota_models)}] Dropping table: {table_name}")
            message_dispatcher.notify_info_message(f"Dropping table {table_name}")

            try:
                # Check if table exists and has data
                if not biota_model.table_exists():
                    Logger.info(f"  Table {table_name} doesn't exist, skipping")
                    continue

                try:
                    record_count = biota_model.select().count()
                    Logger.info(f"  Table {table_name} has {record_count} records before drop")
                except:
                    Logger.info(f"  Table {table_name} exists but is inaccessible")

                # Drop the table
                biota_model.drop_table()
                Logger.info(f"  ✓ Table {table_name} dropped successfully")

            except Exception as e:
                Logger.error(f"  ✗ Error dropping table {table_name}: {e}")
                raise

        # Commit changes before re-enabling constraints
        Logger.info("Committing changes...")
        BiotaDbManager.db.commit()
        Logger.info("✓ Changes committed")

        Logger.info("Re-enabling foreign key checks...")
        BiotaDbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        Logger.info("✓ Foreign key checks re-enabled")

        BiotaDbManager._DEACTIVATE_PROTECTION_ = False

        Logger.info("=" * 80)
        Logger.info(f"SUCCESSFULLY DROPPED {len(biota_models)} TABLES")
        Logger.info("=" * 80)

    @classmethod
    def create_biota_tables(cls, biota_models: list[type[Base]], message_dispatcher: MessageDispatcher = None) -> None:
        """
        Create biota tables with detailed logging

        :param biota_models: List of model classes to create
        :param message_dispatcher: Optional message dispatcher for UI feedback
        """
        Logger.info("=" * 80)
        Logger.info("CREATING BIOTA TABLES")
        Logger.info("=" * 80)

        BiotaDbManager._DEACTIVATE_PROTECTION_ = True

        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        BiotaDbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")

        for idx, biota_model in enumerate(biota_models, 1):
            table_name = biota_model.__name__
            Logger.info(f"[{idx}/{len(biota_models)}] Creating table: {table_name}")
            message_dispatcher.notify_info_message(f"Creating table {table_name}")

            try:
                biota_model.create_table()
                Logger.info(f"  ✓ Table {table_name} created successfully")

                # Verify table is empty
                try:
                    record_count = biota_model.select().count()
                    if record_count > 0:
                        Logger.warning(f"  ⚠ WARNING: Table {table_name} has {record_count} records after creation!")
                    else:
                        Logger.info(f"  ✓ Table {table_name} is empty")
                except Exception as e:
                    Logger.debug(f"  Could not verify table emptiness: {e}")

            except Exception as e:
                Logger.error(f"  ✗ Error creating table {table_name}: {e}")
                raise

        for biota_model in biota_models:
            if hasattr(biota_model, 'after_all_tables_init'):
                Logger.info(f"Running after_all_tables_init for {biota_model.__name__}")
                biota_model.after_all_tables_init()

        BiotaDbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        BiotaDbManager._DEACTIVATE_PROTECTION_ = False

        Logger.info("=" * 80)
        Logger.info(f"SUCCESSFULLY CREATED {len(biota_models)} TABLES")
        Logger.info("=" * 80)

    @staticmethod
    def check_null_columns(model, columns: list, task_name: str = "") -> None:
        """
        For each column name in the list, checks if ALL rows in the table have NULL.
        If any column is entirely NULL, raises an Exception to fail the task.
        Skips the check if the table is empty (other checks will catch that).

        :param model: Peewee model class
        :param columns: List of column names (strings) to verify
        :param task_name: Name of the creator task for error messages
        """
        from peewee import fn

        try:
            total = model.select().count()
        except Exception as e:
            Logger.warning(f"check_null_columns: could not count rows in {model.__name__}: {e}")
            return

        if total == 0:
            # Table empty — let other checks raise the error
            return

        all_null_columns = []
        for col_name in columns:
            try:
                field = getattr(model, col_name)
                non_null_count = model.select(fn.COUNT(field)).scalar()
                if non_null_count == 0:
                    Logger.error(f"  ✗ Column '{col_name}' in {model.__name__}: ALL {total} rows are NULL!")
                    all_null_columns.append(col_name)
                else:
                    Logger.info(f"  ✓ Column '{col_name}' in {model.__name__}: {non_null_count}/{total} rows non-NULL")
            except Exception as e:
                Logger.warning(f"  Could not check column '{col_name}' in {model.__name__}: {e}")

        if all_null_columns:
            raise Exception(
                f"[{task_name}] ERROR: The following columns are entirely NULL in {model.__name__} "
                f"({total} rows total): {', '.join(all_null_columns)}. "
                f"This indicates a parsing or format compatibility issue."
            )
