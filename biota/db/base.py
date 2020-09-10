# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import SqliteDatabase, Proxy

from gws.base import DbManager as BaseDbManager
from gws.model import Resource

from gws.settings import Settings

settings = Settings.retrieve()
db_dir = settings.get_dir("biota:db_dir")
db_name = settings.get_data("db_name")
biota_db_path = os.path.join(db_dir, db_name)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

class DbManager(BaseDbManager):
    """
    DbManager class. Provides backend feature for managing databases. 
    """

    db = SqliteDatabase(biota_db_path)  #redirect to a separate defautl db

class Base(Resource):

    class Meta:
        database = DbManager.db