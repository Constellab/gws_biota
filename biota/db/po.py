# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import ForeignKeyField, CharField
from biota.db.entity import Entity

class PO(Entity):
    """
    This class represents protein ortholog.
    """

    ec_number = CharField(null=True, index=True)
    ko = CharField(null=True, index=True)
    
    _table_name = 'po'
