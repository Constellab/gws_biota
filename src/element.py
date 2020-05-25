import unittest #not sure if necessary
import copy #not sure if necessary
from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Resource
from gws.prism.controller import Controller
from peewee import IntegerField

####################################################################################
#
# Element class
#
####################################################################################

class Element(Resource):
    GO_id = IntegerField(primary_key=True)
    SBO_id = IntegerField(primary_key=True)
    _table_name = 'element'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        table_name = 'element'