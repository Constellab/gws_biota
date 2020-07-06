import os, sys
from biota.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked, ForeignKeyField, ManyToManyField, DeferredThroughModel, DeferredForeignKey
from peewee import Model as PWModel
from onto.ontology import Onto
from biota.ontology import Ontology
from peewee import CharField, chunked

####################################################################################
#
# SBO class
#
####################################################################################

class SBO(Ontology):
    sbo_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'sbo'
    
    #Setters
    def set_definition(self, def__):
        self.definition = def__

    def set_name(self, name__):
        self.name = name__    

    def set_sbo_id(self, id):
        self.sbo_id = id
    
    def __get_ancestors_query(self):
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.sbo_id):
                val = {'sbo': self.id, 'ancestor': SBO.get(SBO.sbo_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)
    
    #Inserts
    def insert_definition(list__, key):
        for sbo in list__:
            sbo.set_definition(sbo.data[key])
    
    def insert_name(list__, key):
        for sbo in list__:
            sbo.set_name(sbo.data[key])

    def insert_sbo_id(list__, key):
        for sbo in list__:
            sbo.set_sbo_id(sbo.data[key])    
    
    #Create and drop methods
    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        SBOAncestor.create_table()

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        SBOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)


    #create sbo
    @classmethod
    def create_sbo(cls, input_db_dir, **files):
        Onto.correction_of_SBO_OBO_file(input_db_dir, files["sbo_data"], 'SBO_out_test.obo')
        ontology = Onto.create_ontology_from_owl(input_db_dir, 'SBO_out_test.obo')
        list_sbo = Onto.parse_sbo_terms_from_ontology(ontology)

        sbos = [cls(data = dict_) for dict_ in list_sbo]
        cls.insert_sbo_id(sbos,"id")
        cls.insert_name(sbos, "name")
        cls.insert_definition(sbos, "definition")
        Controller.save_all()

        vals = []
        for sbo in sbos:
            if ('ancestors' in sbo.data.keys()):
                val = sbo.__get_ancestors_query()
                if len(val) != 0:
                    for v in val:
                        vals.append(v)
        SBOAncestor.insert_many(vals).execute()

        return(list_sbo)

    class Meta():
        table_name = 'sbo'

class SBOAncestor(PWModel):
    sbo = ForeignKeyField(SBO)
    ancestor = ForeignKeyField(SBO)
    class Meta:
        table_name = 'sbo_ancestors'
        database = DbManager.db
        indexes = (
            (('sbo', 'ancestor'), True),
        )

class SBOJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id": {{view_model.model.sbo_id}} , "name": {{view_model.model.name}}, "definition": {{view_model.model.definition}} }')