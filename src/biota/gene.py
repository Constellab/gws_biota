import os, sys
from biota.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked


####################################################################################
#
# Gene class
#
####################################################################################

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Gene(Entity):
    KO = CharField(null=True, index=True)
    _table_name = 'gene'

    def set_KO(self, ko):
        self.KO = ko
    pass

    class Meta():
        table_name = 'gene'

class GeneHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class GeneJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate("ID: {{view_model.model.data.ID}}")

Gene.register_view_models([
    GeneHTMLViewModel, 
    GeneJSONViewModel
])

Controller.register_models([
    Gene,
    GeneHTMLViewModel,
    GeneJSONViewModel
])

