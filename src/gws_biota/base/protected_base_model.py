


from gws_core import BaseModel, Logger
from peewee import chunked

from ..db.biota_db_manager import BiotaDbManager

IS_IPYTHON_ACTIVE = False
try:
    get_ipython
    IS_IPYTHON_ACTIVE = True
except:
    pass


class ProtectedBaseModel(BaseModel):

    _is_table_warning_printed = False

    BATCH_SIZE = 10000

    # -- C --

    @classmethod
    def inheritors(cls):
        """ Get all the classes that inherit this class """
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.inheritors()])

    @classmethod
    def create_all(cls, model_list: list['ProtectedBaseModel'], batch_size=BATCH_SIZE, use_transaction=True) -> list['ProtectedBaseModel']:
        """
        Automically and safely save a list of models in the database. If an error occurs
        during the operation, the whole transactions is rolled back (if use_transaction=True).

        :param model_list: List of models
        :type model_list: list
        :param batch_size: Size of each batch for bulk creation
        :type batch_size: int
        :param use_transaction: If True, wraps all batches in a single transaction.
                                 If False, each batch creates its own transaction (for MariaDB timeout issues)
        :type use_transaction: bool
        :return: True if all the model are successfully saved, False otherwise.
        :rtype: bool
        """
        if not model_list:
            Logger.warning(f"{cls.__name__}.create_all: No items to create")
            return model_list

        Logger.info(f"{cls.__name__}.create_all: Creating {len(model_list)} items (batch size: {batch_size}, transaction: {use_transaction})")

        total_created = 0
        num_batches = (len(model_list) + batch_size - 1) // batch_size

        db = cls.get_db()

        if use_transaction:
            # Original behavior: wrap all batches in one transaction
            with db.atomic():
                for i in range(0, len(model_list), batch_size):
                    batch = model_list[i:i + batch_size]
                    batch_num = (i // batch_size) + 1

                    try:
                        cls.bulk_create(batch, batch_size=batch_size)
                        total_created += len(batch)
                    except Exception as e:
                        Logger.error(f"  ✗ Batch {batch_num}/{num_batches}: Error during creation!")
                        Logger.error(f"    Error: {type(e).__name__}: {str(e)}")
                        if batch:
                            Logger.error(f"    First item: {batch[0].__data__}")
                        raise
        else:
            # No global transaction: each bulk_create() uses its own internal transaction
            # This prevents MariaDB timeout on very large datasets
            for i in range(0, len(model_list), batch_size):
                batch = model_list[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                try:
                    cls.bulk_create(batch, batch_size=batch_size)
                    total_created += len(batch)
                except Exception as e:
                    Logger.error(f"  ✗ Batch {batch_num}/{num_batches}: Error during creation!")
                    Logger.error(f"    Error: {type(e).__name__}: {str(e)}")
                    if batch:
                        Logger.error(f"    First item: {batch[0].__data__}")
                    raise

        Logger.info(f"{cls.__name__}.create_all: ✓ Completed - {total_created} items created")

        return model_list

    @classmethod
    def update_all(cls, model_list: list['ProtectedBaseModel'],
                   fields: list, batch_size=BATCH_SIZE, use_transaction=True) -> list['ProtectedBaseModel']:
        """
        Automically and safely save a list of models in the database. If an error occurs
        during the operation, the whole transactions is rolled back (if use_transaction=True).

        :param model_list: List of models
        :type model_list: list
        :param use_transaction: If True, wraps bulk_update in a transaction.
                                 If False, bulk_update handles its own transactions (for MariaDB timeout issues)
        :type use_transaction: bool
        :return: True if all the model are successfully saved, False otherwise.
        :rtype: bool
        """

        db = cls.get_db()
        if use_transaction:
            with db.atomic():
                cls.bulk_update(model_list, fields, batch_size=batch_size)
        else:
            cls.bulk_update(model_list, fields, batch_size=batch_size)

        return model_list

    @classmethod
    def insert_all(cls, data: list['ProtectedBaseModel'], batch_size=BATCH_SIZE, use_transaction=True) -> None:
        """
        Insert multiple items with detailed logging

        :param data: List of dictionaries to insert
        :param batch_size: Number of items per batch
        :param use_transaction: If True, wraps all batches in a single transaction.
                                 If False, each batch uses its own transaction (for MariaDB timeout issues)
        :type use_transaction: bool
        """
        if not data:
            Logger.warning(f"{cls.__name__}.insert_all: No items to insert")
            return

        Logger.info(f"{cls.__name__}.insert_all: Inserting {len(data)} items (batch size: {batch_size}, transaction: {use_transaction})")

        total_inserted = 0
        num_batches = (len(data) + batch_size - 1) // batch_size

        db = cls.get_db()

        if use_transaction:
            # Original behavior: wrap all batches in one transaction
            with db.atomic():
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    batch_num = (i // batch_size) + 1

                    try:
                        cls.insert_many(batch).execute()
                        total_inserted += len(batch)
                    except Exception as e:
                        Logger.error(f"  ✗ Batch {batch_num}/{num_batches}: Error during insertion!")
                        Logger.error(f"    Error: {type(e).__name__}: {str(e)}")
                        if batch:
                            Logger.error(f"    First item: {batch[0] if batch else 'N/A'}")
                        raise
        else:
            # No global transaction: each insert_many() uses its own internal transaction
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                try:
                    cls.insert_many(batch).execute()
                    total_inserted += len(batch)
                except Exception as e:
                    Logger.error(f"  ✗ Batch {batch_num}/{num_batches}: Error during insertion!")
                    Logger.error(f"    Error: {type(e).__name__}: {str(e)}")
                    if batch:
                        Logger.error(f"    First item: {batch[0] if batch else 'N/A'}")
                    raise

        Logger.info(f"{cls.__name__}.insert_all: ✓ Completed - {total_inserted} items inserted")

        # Verify insertion
        try:
            final_count = cls.select().count()
            Logger.info(f"{cls.__name__}: Current total records in table: {final_count}")
        except Exception as e:
            Logger.debug(f"{cls.__name__}: Could not verify final count: {e}")

    @classmethod
    def _is_protected(cls):
        # always protect in notebooks
        if IS_IPYTHON_ACTIVE:
            cls._print_warning("The BIOTA db is protected in notebooks")
            return True

        db_manager: BiotaDbManager = cls.get_db_manager()
        # always protect in prod mode
        if db_manager.mode == "prod":
            cls._print_warning("The prod BIOTA db is protected and cannot be altered")
            return True

        # check protection in dev mode
        if db_manager.mode == "dev":
            if hasattr(db_manager, "_DEACTIVATE_PROTECTION_") and db_manager._DEACTIVATE_PROTECTION_:
                cls._print_warning("The BIOTA protection is DEACTIVATED")
                return False
            else:
                cls._print_warning("The dev BIOTA db is protected and cannot be altered")
                return True

        return False

    @classmethod
    def _print_warning(cls, msg):
        if not ProtectedBaseModel._is_table_warning_printed:
            Logger.warning(msg)
            ProtectedBaseModel._is_table_warning_printed = True

    @classmethod
    def create_table(cls, *args, **kwargs):
        if cls._is_protected():
            return
        super().create_table(*args, **kwargs)

    # -- D --

    @classmethod
    def delete(cls, *args, **kwargs):
        if cls._is_protected():
            return False
        return super().delete(*args, **kwargs)

    @classmethod
    def drop_table(cls, *args, **kwargs):
        if cls._is_protected():
            return
        super().drop_table(*args, **kwargs)

    # -- S --

    def save(self, *args, **kwargs):
        if self._is_protected():
            return False
        return super().save(*args, **kwargs)

    class Meta:
        db_manager = BiotaDbManager.get_instance()
        is_table = False
        database = db_manager.db
