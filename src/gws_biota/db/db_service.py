# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import List, Type
from gws_core import (BaseService, MessageDispatcher)
from gws_biota.base.base import Base
from .db_manager import DbManager


class DbService(BaseService):
    @classmethod
    def drop_biota_tables(cls, biota_models: List[Type[Base]], message_dispatcher: MessageDispatcher = None) -> None:
        """
        Drops tables (if they exist)

        :param models: List of model tables to drop
        :type models: `List[type]`
        :param instance: If provided, only the tables of the models that are instances of `model_type` will be droped
        :type model_type: `type`
        """
        DbManager._DEACTIVATE_PROTECTION_ = True

        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        # Disable foreigne key on my sql to drop the tables
        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        for biota_model in biota_models:

            if not biota_model.table_exists():
                continue

            # Drop all the tables
            message_dispatcher.notify_info_message(f"Dropping table {biota_model.__name__}")
            biota_model.drop_table()

        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        DbManager._DEACTIVATE_PROTECTION_ = False

    @classmethod
    def create_biota_tables(cls, biota_models: List[Type[Base]], message_dispatcher: MessageDispatcher = None) -> None:
        DbManager._DEACTIVATE_PROTECTION_ = True

        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        for biota_model in biota_models:
            message_dispatcher.notify_info_message(f"Creating table {biota_model.__name__}")
            biota_model.create_table()

        for biota_model in biota_models:
            if hasattr(biota_model, 'after_all_tables_init'):
                biota_model.after_all_tables_init()

        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
        DbManager._DEACTIVATE_PROTECTION_ = False
