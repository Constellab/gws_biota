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

    name = CharField(null=True, index=True)
    _table_name = 'pathway'

    # -- C --

    # -- S -- 
