import unittest #not sure if necessary
import copy #not sure if necessary
import sys
import os
import unittest

from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from peewee import IntegerField, DateField, DateTimeField, CharField, ForeignKeyField

from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# Ontology class
#
####################################################################################

class Ontology(Resource):
    _table_name = 'ontology'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Meta():
    table_name = 'ontology'