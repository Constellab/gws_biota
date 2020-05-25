from gws.settings import Settings
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.controller import Controller


####################################################################################
#
# Reaction class
#
####################################################################################


class Reaction(Resource):
    pass

class ReactionHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class ReactionJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id":"{{view_model.model.data.ID}}"}')

Reaction.register_view_models([
    ReactionHTMLViewModel, 
    ReactionJSONViewModel
])

Controller.register_models([
    Reaction,
    ReactionHTMLViewModel,
    ReactionJSONViewModel
])