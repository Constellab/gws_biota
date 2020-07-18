from gws.prism.model import Resource, ResourceViewModel
from gws.prism.view import JSONViewTemplate
from peewee import CharField

####################################################################################
#
# Pathway class
#
####################################################################################

class Pathway(Resource):
    path_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    compartments = CharField(null=True, index=True)
    version = CharField(null=True, index=True)
    _table_name = 'pathway'

    # -- S -- 
    
    def set_path_id(self, id):
        self.path_id = id

    def set_name(self, name):
        self.name = name

    def set_compartments(self, comps):
        self.compartments = comps

    def ser_version(self, version):
        self.version = version

    class Meta():
        table_name = 'pathway'
        
class PathwayJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id": {{view_model.model.path_id}}, "name": {{view_model.model.name}},"compartments": {{view_model.model.compartments}}, "version": {{view_model.model.compartments}} }') 