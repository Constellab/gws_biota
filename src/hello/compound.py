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
    
    def create_table_from_csv_file(self, file):
        with open(path_test + '\\' + file) as csv_file:
            csv_reader = csv.reader(csv_file)
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

                    if(len(list_row) == len(infos_table)):
                        for i in range(0, len(infos_table)):
                            dict_compound[infos_table[i]] = list_row[i] 

                    else:   
                        for i in range(0, len(list_row)):
                            dict_compound[infos_table[i]] = list_row[i]

                    list_compound.append(dict_compound)
                    line_count += 1

                    #Creation of compound 
                    Compound.create(data = dict_compound)

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

class Meta:
    table_name = 'compound'


