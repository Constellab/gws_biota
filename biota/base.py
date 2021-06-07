# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import pymysql
from peewee import SqliteDatabase, MySQLDatabase, DatabaseProxy
from peewee import CharField
from playhouse.sqlite_ext import JSONField as SQLiteJSONField
from playhouse.mysql_ext import JSONField as MySQLJSONField

from gws.db.model import AbstractDbManager
from gws.model import Resource
from gws.settings import Settings
from gws.logger import Error

settings = Settings.retrieve()

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
    JSONField = None
    _engine = None
    _db_name = "biota"

    @classmethod
    def use_prod_db(cls, tf:bool):
        if tf:
            DbManager.init(mode="prod")
        else:
            DbManager.init(mode="dev")

DbManager.init()

# ####################################################################
#
# Base class
#
# ####################################################################

class Base(Resource):
    
    name = CharField(null=True, index=True)
    #_fts_fields = { 'title': 2.0 }
    
    @classmethod
    def fts_model(cls):
        _FTSModel = super().fts_model()
        if _FTSModel:
            _FTSModel._meta.database = DbManager.db
        return _FTSModel
    
    # -- C --
    
    @classmethod
    def create_table(cls, *arg, **kwargs):
        #if is_prod_db:
        #    raise Error("biota.Base", "create_table", "Cannot alter the prodution database")
        super().create_table(*arg, **kwargs)
    
    # -- D --
    
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        #if is_prod_db:
        #    raise Error("biota.Base", "create_table", "Cannot alter the prodution database")
            
        super().drop_table(*arg, **kwargs)
    
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
    
    #def save(self, *arg, **kwargs):
    #    if is_prod_db:
    #        raise Error("biota.Base", "create_table", "Cannot alter the prodution database")
    #    
    #    return super().save(*arg, **kwargs)
    
    class Meta:
        database = DbManager.db