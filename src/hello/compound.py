import os, sys
from hello.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField
#from tables import table_test as TAB

import csv
####################################################################################
#
# Compound class
#
####################################################################################
path_test = os.path.realpath('./databases_input')
class Compound(Entity):
    name = CharField(null=True)
    
    def OpenFile(self, file):
        with open(path_test+'\\table_test.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            status = 'test ok'
        return(status)


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


