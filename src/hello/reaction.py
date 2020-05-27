from gws.settings import Settings
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.controller import Controller
from hello.relation import Relation

####################################################################################
#
# Reaction class
#
####################################################################################


class Reaction(relation):
    COUMPOUND_list = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    _table_name = 'reaction'

    def get_coumpound(self):
        pass


class Meta
    table_name = 'reaction'
