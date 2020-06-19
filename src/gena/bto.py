import os, sys
from gena.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, ForeignKeyField, chunked, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel
from gena.ontology import Ontology
from onto.ontology import Onto
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# BTO class
#
####################################################################################
BTOAncestorsDeferred = DeferredThroughModel()

class BTO(Ontology):
    bto_id = CharField(null=True, index=True)
    label = CharField(null=True, index=True)
    ancestors = CharField(null=True, index=True)
    #ancestors = ManyToManyField('self', backref='is_ancestor_of', through_model = BTOAncestorsDeferred)
    _table_name = 'bto'

    #Setters
    def set_bto_id(self, id):
        self.bto_id = id

    def set_label(self, label_):
        self.label = label_ 
    
    def set_ancestors(self, ancestors_):
        self.ancestors = ancestors_

    """
    def set_ancestors(self):
        for i in range(0,len(self.data['ancestors'])):
            an = BTO.get(BTO.bto_id == self.data['ancestors'][i])
            #self.ancestors =  ManyToManyField(BTO, backref='is_ancestor_of', through_model = BTOAncestorsDeferred)
            self.ancestors.add(an)
    """

    #Inserts
    def insert_bto_id(list__, key):
        for bto in list__:
            bto.set_bto_id(bto.data[key]) 

    def insert_label(list__, key):
        for bto in list__:
            bto.set_label(bto.data[key]) 

    def insert_ancestors(list__, key):
        for bto in list__:
            bto.set_ancestors(bto.data[key])

    
    #create bto
    @classmethod
    def create_bto(cls, input_db_dir, **files):
        list_bto = Onto.parse_bto_from_json(input_db_dir, files['bto_json_data'])
        btos = [cls(data = dict_) for dict_ in list_bto]
        cls.insert_bto_id(btos,"id")
        cls.insert_label(btos, "label")
        #cls.def_ancestors(btos)
        cls.insert_ancestors(btos, "ancestors")
        Controller.save_all()
        return(list_bto)

    """
    def def_ancestors(cls,btos):
        for bt in btos:
            cls.set_ancestors()
    """
    
    class Meta():
        table_name = 'bto'

class BTOAncestors(PWModel):
    ancestors = ForeignKeyField(BTO)
    tissue = ForeignKeyField(BTO)
    class Meta:
        table_name = 'bto_ancestors'
        database = DbManager.db

BTOAncestorsDeferred.set_model(BTOAncestors)