import os, sys
from biota.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel, ResourceViewModel, Resource, Process, DbManager
from peewee import CharField, Model, chunked, ForeignKeyField, ManyToManyField, DeferredThroughModel, DeferredForeignKey
from peewee import Model as PWModel
from biota.ontology import Ontology
from onto.ontology import Onto
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# GO class
#
####################################################################################

class GO(Ontology):
    go_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    namespace = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'go'
    pass

    #Setters
    def set_definition(self, def__):
        self.definition = def__

    def set_go_id(self, id):
        self.go_id = id

    def set_name(self, name__):
        self.name = name__
    
    def set_namespace(self, namespace__):
        self.namespace = namespace__
    
    def __get_ancestors_query(self):
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.go_id):
                val = {'go': self.id, 'ancestor': GO.get(GO.go_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)
    
    #Inserts
    def insert_definition(list__, key):
        for go in list__:
            go.set_definition(go.data[key])

    def insert_go_id(list__, key):
        for go in list__:
            go.set_go_id(go.data[key])

    def insert_name(list__, key):
        for go in list__:
            go.set_name(go.data[key])

    def insert_namespace(list__, key):
        for go in list__:
            go.set_namespace(go.data[key])

    # Create and drop methods
    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        GOAncestor.create_table()

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        GOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    #create go
    @classmethod
    def create_go(cls, input_db_dir, **files_test):
        onto_go = Onto.create_ontology_from_obo(input_db_dir, files_test["go_data"])
        list_go = Onto.parse_obo_from_ontology(onto_go)
        gos = [cls(data = dict_) for dict_ in list_go]
        cls.insert_go_id(gos,"id")
        cls.insert_name(gos, "name")
        cls.insert_namespace(gos, "namespace")
        cls.insert_definition(gos, "definition")
        Controller.save_all()

        vals = []
        for go in gos:
            if ('ancestors' in go.data.keys()):
                val = go.__get_ancestors_query()
                if len(val) != 0:
                    for v in val:
                        vals.append(v)
        GOAncestor.insert_many(vals).execute()
        return(list_go)

    class Meta():
        table_name = 'go'

class GOAncestor(PWModel):
    go = ForeignKeyField(GO)
    ancestor = ForeignKeyField(GO)
    class Meta:
        table_name = 'go_ancestors'
        database = DbManager.db
        indexes = (
            (('go', 'ancestor'), True),
        )

class GOJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id": {{view_model.model.go_id}} , "name": {{view_model.model.name}} }')
    
class GOJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id": {{view_model.model.go_id}} , "name": {{view_model.model.name}}, "namespace": {{view_model.model.namespace}} , "definition": {{view_model.model.definition}} }')