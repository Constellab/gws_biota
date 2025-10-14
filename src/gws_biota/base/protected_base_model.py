

from typing import List

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
    def create_all(cls, model_list: List['ProtectedBaseModel'], batch_size=BATCH_SIZE) -> List['ProtectedBaseModel']:
        """
        Automically and safely save a list of models in the database. If an error occurs
        during the operation, the whole transactions is rolled back.

        :param model_list: List of models
        :type model_list: list
        :return: True if all the model are successfully saved, False otherwise.
        :rtype: bool
        """

        db = cls.get_db()
        with db.atomic():
            cls.bulk_create(model_list, batch_size=batch_size)

        return model_list

    @classmethod
    def update_all(cls, model_list: List['ProtectedBaseModel'],
                   fields: list, batch_size=BATCH_SIZE) -> List['ProtectedBaseModel']:
        """
        Automically and safely save a list of models in the database. If an error occurs
        during the operation, the whole transactions is rolled back.

        :param model_list: List of models
        :type model_list: list
        :return: True if all the model are successfully saved, False otherwise.
        :rtype: bool
        """

        db = cls.get_db()
        with db.atomic():
            cls.bulk_update(model_list, fields, batch_size=batch_size)

        return model_list

    @classmethod
    def insert_all(cls, data: List['ProtectedBaseModel'], batch_size=BATCH_SIZE) -> None:
        db = cls.get_db()
        with db.atomic():
            for batch in chunked(data, batch_size):
                cls.insert_many(batch).execute()

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
