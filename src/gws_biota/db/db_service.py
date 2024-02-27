# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import List, Type

from gws_core import (BadRequestException, BaseService, Experiment, Logger,
                      MessageDispatcher, ModelService)
from gws_core.extra import BaseModelService

from bricks.other.gws_biota.src.gws_biota.base.base import Base
from bricks.other.gws_biota.src.gws_biota.base.protected_base_model import \
    ProtectedBaseModel

from ..eco.eco import ECO, ECOAncestor
from .db_manager import DbManager


class DbService(BaseService):

    # @classmethod
    # def build_biota_db(cls, user=None) -> None:
    #     """
    #     Build biota db
    #     """

    #     cls.create_tables()
    #     DbCreator.run()
    #     Logger.info("Done")

    @classmethod
    def create_tables(cls):
        """
        Create tables
        """

        DbManager.init(mode="dev")
        DbManager._DEACTIVATE_PROTECTION_ = True

        if ECO.table_exists():
            BaseModelService.drop_tables()

        if ECO.table_exists():
            if ECO.select().count():
                raise BadRequestException("A none empty biota database already exists")

        BaseModelService.drop_tables()
        BaseModelService.create_tables()
        ModelService.register_all_processes_and_resources()

        if not ECO.table_exists():
            raise BadRequestException("Cannot create tables")

        if not ECOAncestor.table_exists():
            raise BadRequestException("Cannot create ancestor tables")

    @classmethod
    def reset_tables(cls, biota_models: List[Type[Base]], message_dispatcher: MessageDispatcher = None) -> None:
        """
        Create tables
        """
        if message_dispatcher is None:
            message_dispatcher = MessageDispatcher()

        model_names = [model.__name__ for model in biota_models]

        message_dispatcher.notify_info_message(f"Initializing biota tables {model_names}")
        DbManager._DEACTIVATE_PROTECTION_ = True

        biota_models = ProtectedBaseModel.inheritors()

        message_dispatcher.notify_info_message("Deleting biota tables")
        try:
            cls.drop_biota_tables(biota_models, message_dispatcher=message_dispatcher)
        except Exception as err:
            message_dispatcher.notify_error_message(f'Error during drop, recreating tables. Error: {err}')
            cls.create_biota_tables(biota_models)
            raise err

        message_dispatcher.notify_info_message("Creating biota tables")
        cls.create_biota_tables(biota_models)

        for model in biota_models:
            if not model.table_exists():
                raise BadRequestException(f"Cannot create table {model.__name__}")

        DbManager._DEACTIVATE_PROTECTION_ = False

        message_dispatcher.notify_info_message(f"Biota tables {model_names} initialized")

    @classmethod
    def drop_biota_tables(cls, biota_models: List[Type[Base]], message_dispatcher: MessageDispatcher = None):
        """
        Drops tables (if they exist)

        :param models: List of model tables to drop
        :type models: `List[type]`
        :param instance: If provided, only the tables of the models that are instances of `model_type` will be droped
        :type model_type: `type`
        """
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

    @classmethod
    def create_biota_tables(cls, biota_models: List[Type[Base]]):
        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        for biota_model in biota_models:
            biota_model.create_table()

        for biota_model in biota_models:
            if hasattr(biota_model, 'after_all_tables_init'):
                biota_model.after_all_tables_init()

        DbManager.db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
