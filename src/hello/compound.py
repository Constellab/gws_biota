from hello.entity import Entity
from gws.prism.controller import Controller


####################################################################################
#
# Compound class
#
####################################################################################

class Compound(Entity):
     name = CharField(null=True)
    pass

class CompoundHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class CompoundJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id":"{{view_model.model.data.ID}}"}')

Compound.register_view_models([
    CompoundHTMLViewModel, 
    CompoundJSONViewModel
])

Controller.register_models([
    Compound,
    CompoundHTMLViewModel,
    CompoundJSONViewModel
])