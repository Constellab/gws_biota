# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import ForeignKeyField, CharField
from gws.controller import Controller
from biota.db.entity import Entity

class Enzyme(Entity):
    """
    This class represents proteins.
    """

    name = CharField(null=True, index=True)
    _table_name = 'protein'

    @classmethod
    def create_protein_db(cls, biodata_dir = None, **kwargs):
        from biota.db.enzyme import Enzyme
        Enzyme.create_enzyme_db(biodata_dir = biodata_dir, **kwargs)
