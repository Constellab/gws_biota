# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import ForeignKeyField, CharField
from gws.prism.controller import Controller
from biota._helper.brenda import Brenda
from biota.db.entity import Entity

class Protein(Entity):
    """
    This class represents proteins.
    """

    name = CharField(null=True, index=True)
    uniprot_id = CharField(null=True, index=True)
    _table_name = 'protein'

    @classmethod
    def create_protein_db(cls, biodata_db_dir, **files):
        from biota.db.enzyme import Enzyme
        Enzyme.create_enzyme_db(biodata_db_dir, **files)

    class Meta():
        table_name = 'protein'


Controller.register_model_classes([Protein])