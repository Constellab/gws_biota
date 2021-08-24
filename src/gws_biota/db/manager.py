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
    _DEFAULT_DB_ENGINE = "sqlite3"
    _DEFAULT_DB_NAME = "gws_biota"
    _engine = None
    _mariadb_config = {
        "user": _DEFAULT_DB_NAME,
        "password": "gencovery"
    }
    _db_name = _DEFAULT_DB_NAME
    