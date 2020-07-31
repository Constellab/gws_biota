# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField

from gws.prism.controller import Controller
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.view import JSONViewTemplate

class Pathway(Resource):
    """
    This class represents biological pathways
    """

    pathway_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    compartments = CharField(null=True, index=True)
    version = CharField(null=True, index=True)
    _table_name = 'pathway'

    # -- S -- 
    
    def set_pathway_id(self, id):
        """
        Sets the is of the pathway

        :param id: The id
        :type id: str
        """

        self.pathway_id = id

    def set_name(self, name):
        """
        Sets the name of the pathway

        :param name: The name
        :type name: str
        """

        self.name = name

    def set_compartments(self, comps):
        """
        Sets the compartments of the pathway

        :param compartments: The compartments
        :type compartments: list
        """

        self.compartments = comps

    def ser_version(self, version):
        """
        Sets the version of the pathway

        :param version: The version
        :type version: str
        """

        self.version = version

    class Meta():
        table_name = 'pathway'
        
class PathwayJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id": {{view_model.model.pathway_id}}, "name": {{view_model.model.name}},"compartments": {{view_model.model.compartments}}, "version": {{view_model.model.compartments}} }') 

Controller.register_model_classes([Pathway])