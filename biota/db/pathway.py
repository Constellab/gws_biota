# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField
from gws.prism.model import Resource

from biota.db.base import Base

class Pathway(Base):
    """
    This class represents biological pathways
    """

    name = CharField(null=True, index=True)
    _table_name = 'pathway'

    # -- C --

    # -- S -- 
