import os, sys
from hello.protein import Protein 
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked

####################################################################################
#
# Enzyme class
#
####################################################################################

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Enzyme(Protein):
    _table_name = 'enzyme'
    pass

class EnzymeHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class EnzymeJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id":"{{view_model.model.data.ID}}"}')

Enzyme.register_view_models([
    EnzymeHTMLViewModel, 
    EnzymeJSONViewModel
])

Controller.register_models([
    Enzyme,
    EnzymeHTMLViewModel,
    EnzymeJSONViewModel
])

class Meta():
    table_name = 'enzyme'