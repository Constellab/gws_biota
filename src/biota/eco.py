import os, sys
from biota.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel, ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked, ForeignKeyField, ManyToManyField, DeferredThroughModel, DeferredForeignKey
from peewee import Model as PWModel
from biota.ontology import Ontology
from onto.ontology import Onto
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# ECO class
#
####################################################################################

class ECO(Ontology):
    eco_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'eco'
    pass

    #Setters
    def set_definition(self, def__):
        self.definition = def__

    def set_eco_id(self, id):
        self.eco_id = id

    def set_name(self, name__):
        self.name = name__
    
    def __get_ancestors_query(self):
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.eco_id):
                val = {'eco': self.id, 'ancestor': ECO.get(ECO.eco_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)
    
    #Inserts
    def insert_definition(list__, key):
        for eco in list__:
            eco.set_definition(eco.data[key])

    def insert_eco_id(list__, key):
        for eco in list__:
            eco.set_eco_id(eco.data[key])

    def insert_name(list__, key):
        for eco in list__:
            eco.set_name(eco.data[key])
    
    # Create and drop methods
    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        ECOAncestor.create_table()

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        ECOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    
    #create eco
    @classmethod
    def create_eco(cls, input_db_dir, **files_test):
        onto_eco = Onto.create_ontology_from_obo(input_db_dir, files_test["eco_data"])
        list_eco = Onto.parse_eco_terms_from_ontoloy(onto_eco)
        ecos = [cls(data = dict_) for dict_ in list_eco]
        cls.insert_eco_id(ecos,"id")
        cls.insert_name(ecos, "name")
        cls.insert_definition(ecos, "definition")
        Controller.save_all()

        vals = []
        for eco in ecos:
            if ('ancestors' in eco.data.keys()):
                val = eco.__get_ancestors_query()
                if len(val) != 0:
                    for v in val:
                        vals.append(v)
        ECOAncestor.insert_many(vals).execute()
        return(list_eco)

    class Meta():
        table_name = 'eco'

class ECOAncestor(PWModel):
    eco = ForeignKeyField(ECO)
    ancestor = ForeignKeyField(ECO)
    class Meta:
        table_name = 'eco_ancestors'
        database = DbManager.db
        indexes = (
            (('eco', 'ancestor'), True),
        )

class ECOJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id": {{view_model.model.eco_id}} , "name": {{view_model.model.name}}, "definition": {{view_model.model.definition}} }')