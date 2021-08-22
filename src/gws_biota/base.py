# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import pymysql
from peewee import SqliteDatabase, MySQLDatabase, DatabaseProxy
from peewee import CharField

from gws_core.core.db.manager import AbstractDbManager
from gws_core import BadRequestException
from gws_core import Resource, Settings

#BIOTA_DB_ENGINE = "mariadb"
BIOTA_DB_ENGINE="sqlite3"
#BIOTA_DB_ENGINE = os.getenv("LAB_DB_ENGINE", "sqlite3")

# ####################################################################
#
# DbManager class
#
# ####################################################################

settings = Settings.retrieve()
class DbManager(AbstractDbManager):
    """
    DbManager class. 
    
    Provides backend features for managing databases. 
    """
    
    db = DatabaseProxy()
    _engine = None
    _mariadb_config = {
        "user": "gws_biota",
        "password": "gencovery"
    }
    _db_name = "gws_biota"

    @classmethod
    def use_test_db(cls, tf:bool = True):
        if tf:
            DbManager.init(engine=BIOTA_DB_ENGINE, test=True)
        else:
            DbManager.init(engine=BIOTA_DB_ENGINE, test=False)

DbManager.init(engine=BIOTA_DB_ENGINE)

# ####################################################################
#
# Base class
#
# ####################################################################

class Base(Resource):
    
    name = CharField(null=True, index=True)
    _db_manager = DbManager 

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        if settings.is_test and settings.is_prod:
            raise BadRequestException("Cannot create the tables of the production Bitoa DB during unit testing")
        super().create_table(*args, **kwargs)

    # -- D --

    @classmethod
    def drop_table(cls, *args, **kwargs):
        if settings.is_test and settings.is_prod:
            raise BadRequestException("Cannot drop the tables of the production Biota DB during unit testing")
        super().drop_table(*args, **kwargs)

    # -- G --
    
    def get_name(self) -> str:
        """
        Get the name. Alias of :meth:`get_title`

        :param: name: The name
        :type name: str
        """
        
        return self.name
    
    # -- S --
    
    def set_name(self, name: str):
        """
        Set the name.

        :param: name: The name
        :type name: str
        """
        
        self.name = name
    

    @classmethod
    def search_by_name(cls, name, page: int=1, number_of_items_per_page: int=50):
        Q = cls.select().where( cls.name ** name ).paginate(page, number_of_items_per_page)
        return Q
    
    class Meta:
        database = DbManager.db