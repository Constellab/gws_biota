# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import pymysql
from peewee import SqliteDatabase, MySQLDatabase, DatabaseProxy
from peewee import CharField

from gws.db.model import AbstractDbManager
from gws.resource import Resource
from gws.logger import Error

#BIOTA_DB_ENGINE = "mariadb"
#BIOTA_DB_ENGINE="sqlite3"
BIOTA_DB_ENGINE = os.getenv("LAB_DB_ENGINE", "sqlite3")

# ####################################################################
#
# DbManager class
#
# ####################################################################


class DbManager(AbstractDbManager):
    """
    DbManager class. 
    
    Provides backend features for managing databases. 
    """
    
    db = DatabaseProxy()
    _engine = None
    _mariadb_config = {
        "user": "biota",
        "password": "gencovery"
    }
    _db_name = "biota"

    @classmethod
    def use_prod_db(cls, tf:bool):
        if tf:
            DbManager.init(engine=BIOTA_DB_ENGINE, mode="prod")
        else:
            DbManager.init(engine=BIOTA_DB_ENGINE, mode="dev")

DbManager.init(engine=BIOTA_DB_ENGINE)

# ####################################################################
#
# Base class
#
# ####################################################################

class Base(Resource):
    
    name = CharField(null=True, index=True)

    # -- C --

    # -- D --

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