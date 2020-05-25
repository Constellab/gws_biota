import unittest #not sure if necessary
import copy #not sure if necessary
from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from peewee import IntegerField, DateField, DateTimeField, CharField, ForeignKeyField

####################################################################################
#
# Element class
#
####################################################################################

class Element(Resource):
    GO_id = CharField(null=True, index=True)
    SBO_id = CharField(null=True, index=True)
    _table_name = 'element'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        table_name = 'element'