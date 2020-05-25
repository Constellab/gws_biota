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

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Compound(Entity):
    name = CharField(null=True)
    
    def create_table_from_csv_file(self, file):
        with open(path_test + '\\' + file) as csv_file:
            csv_reader = csv.reader(csv_file)
            infos_table = ['ID', 'GO_ID', 'SBO_ID', 'name']
            line_count = 0
            list_compound = []
            for rows in csv_reader:
                if (line_count == 0):
                    infos_table = rows[0].split('\t')
                    line_count +=1
                else:
                    list_row = []
                    list_row = rows[0].split('\t')
                    dict_compound = {}
                    for i in range(0,10):
                        dict_compound[infos_table[i]] = list_row[i]  
                    list_compound.append(dict_compound)
                    line_count += 1

                    #Creation of compound 
                    Compound.create(name = dict_compound['NAME'], data = dict_compound)

            status = 'test ok'
        return(status, list_compound)


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


