# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import DatabaseProxy

from gws_core.core.db.manager import AbstractDbManager

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
        "user": "gws_biota",
        "password": "gencovery"
    }
    _db_name = "gws_biota"
    _DEFAULT_DB_ENGINE = "sqlite3"

    @classmethod
    def init_biota_db(cls, test=False) -> None:
        """ Initialize the biota db """
        cls.init(test=test)