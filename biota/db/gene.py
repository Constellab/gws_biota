# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField

from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate
from gws.prism.model import ResourceViewModel

from biota.db.entity import Entity

class Gene(Entity):
    """
    This class represents genes
    """

    KO = CharField(null=True, index=True)
    _table_name = 'gene'

    def set_KO(self, ko):
        self.KO = ko
    pass

    class Meta():
        table_name = 'gene'

Controller.register_model_classes([Gene])

