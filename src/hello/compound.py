import os, sys
from hello.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked

####################################################################################
#
# Compound class
#
####################################################################################

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Compound(Entity):
    COMPOUND_ID = CharField(null=True, index=True)
    SOURCE = CharField(null=True, index=True)
    SOURCE_ACCESSION = CharField(null=True, index=True)
    _table_name = 'compound'

    def set_compound_id(self, id):
        self.COMPOUND_ID = id

    def set_source(self, source):
        self.SOURCE = source
    
    def set_source_accession(self, source_accession):
        self.SOURCE_ACCESSION = source_accession

    def create_table_from_file(self, file):
        with open(path_test + '\\' + file) as fh:
            line_count = 0
            list_compound = []
            for line in fh.readlines():
                if(line_count < 1):
                    infos_table = line.split('\t')
                    line_count +=1
                else:
                    list_row = []
                    list_row = line.split('\t')
                    dict_compound = {}

                    if(len(list_row) == len(infos_table)):
                        for i in range(0, len(infos_table)):
                             dict_compound[infos_table[i]] = list_row[i]
                    else:
                        for i in range(0, len(list_row)):
                           dict_compound[infos_table[i]] = list_row[i] 
                    
                    list_compound.append(dict_compound)
                    line_count += 1
            compounds = [Compound(data = dict_) for dict_ in list_compound]
            """
            with DbManager.db.atomic():
                #Compound.bulk_create(compounds, batch_size=100)
                #Controller.register_models(compounds)
                #for batch in chunked(list_compound, 100):
                    #Compound.insert_many(batch).execute()
                for idx in range(0, len(list_compound), 100):
                    compounds = [Compound(data = dict__) for dict__ in list_compound[idx:idx+100]]
            """
            
            """
            with DbManager.db.atomic():
                #Compound.bulk_create(list_comp, batch_size = 100)
                for batch in chunked(compounds, 100):
                    #print(batch)
                    for comp in batch:
                        Controller.register_models(comp) 
            """
            status = 'test ok'
        return(compounds)
    
    def create_table_from_dict(self, file, infos = list):
        with open(path_test + '\\' + file) as fh:
            line_count = 0
            list_compound = []
            infos_table = infos

            for line in fh.readlines():
                list_row = []
                list_row = line.split('\t')
                dict_compound = {}
                if(len(list_row) == len(infos_table)):
                    for i in range(0, len(infos_table)):
                            dict_compound[infos_table[i]] = list_row[i]
                else:
                    for i in range(0, len(list_row)):
                        dict_compound[infos_table[i]] = list_row[i] 
                
                list_compound.append(dict_compound)
                line_count += 1
            compounds = [Compound(data = dict_) for dict_ in list_compound]
    
    def insert_compound_id(list__, key):
        for comp in list__:
            comp.set_compound_id(comp.data[key])

    def insert_source(list__, key):
        for comp in list__:
            comp.set_source(comp.data[key])
    
    def insert_source_accession(list__, key):
        for comp in list__:
            comp.set_source_accession(comp.data[key])


class CompoundHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class CompoundJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id":"{{view_model.model.data.ID}}"}')
"""
Compound.register_view_models([
    CompoundHTMLViewModel, 
    CompoundJSONViewModel
])

Controller.register_models([
    Compound,
    CompoundHTMLViewModel,
    CompoundJSONViewModel
])"""


class Meta:
    table_name = 'compound'


