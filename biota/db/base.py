# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import SqliteDatabase, Proxy
from peewee import CharField

from gws.base import DbManager as BaseDbManager
from gws.model import Resource

from gws.settings import Settings

settings = Settings.retrieve()
db_dir = settings.get_dir("biota:db_dir")
db_name = settings.get_data("db_name")

if settings.get_data("prod_biota_db"):
    db_name = "db.sqlite3" #force to use the production biota db

is_prod_db = (db_name == "db.sqlite3")

biota_db_path = os.path.join(db_dir, db_name)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

class DbManager(BaseDbManager):
    """
    DbManager class. 
    
    Provides backend features for managing databases. 
    """

    db = SqliteDatabase(biota_db_path)

class Base(Resource):
    
    name = CharField(null=True, index=True)
    _fts_fields = { 'title': 2.0 }

    @classmethod
    def fts_model(cls):
        _FTSModel = super().fts_model()
        _FTSModel._meta.database = DbManager.db
        return _FTSModel
    
    # -- C --
    
    @classmethod
    def create_table(cls, *arg, **kwargs):
        if is_prod_db:
            raise Error("biota.db.Base", "create_table", "Cannot alter the prodution database")
        super().create_table(*arg, **kwargs)
    
    # -- D --
    
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        if is_prod_db:
            raise Error("biota.db.Base", "create_table", "Cannot alter the prodution database")
            
        super().drop_table(*arg, **kwargs)
    
    # -- G --
    
    def get_name(self) -> str:
        """
        Get the name. Alias of :meth:`get_title`

        :param: name: The name
        :type name: str
        """
        
        return self.get_title()
    
    # -- S --
    
    def set_name(self, name: str):
        """
        Set the name. Alias of :meth:`set_title`

        :param: name: The name
        :type name: str
        """
        
        self.name = name
        self.set_title(name)
    

    @classmethod
    def search_by_name(cls, name, page: int=1, number_of_items_per_page: int=50):
        Q = cls.select().where( cls.name ** name ).paginate(page, number_of_items_per_page)
        return Q
    
    #def save(self, *arg, **kwargs):
    #    if is_prod_db:
    #        raise Error("biota.db.Base", "create_table", "Cannot alter the prodution database")
    #    
    #    return super().save(*arg, **kwargs)
    
    class Meta:
        database = DbManager.db