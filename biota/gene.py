# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField
from biota.entity import Entity

class Gene(Entity):
    """
    This class represents genes
    """

    KO = CharField(null=True, index=True)
    _table_name = 'biota_gene'

    def set_KO(self, ko):
        self.KO = ko
