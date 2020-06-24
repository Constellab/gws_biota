import os, sys
from gena.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, ForeignKeyField, chunked, ManyToManyField, DeferredThroughModel, DeferredForeignKey
from peewee import Model as PWModel
from gena.ontology import Ontology
from onto.ontology import Onto
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# BTO class
#
####################################################################################

class BTO(Ontology):
    bto_id = CharField(null=True, index=True)
    label = CharField(null=True, index=True)
    #ancestors = CharField(null=True, index=True)
    #ancestors = ManyToManyField('self', backref='is_ancestor_of', through_model = BTOAncestorsDeferred)
    #ancestors = DeferredForeignKey('BTOAncestor', backref='is_ancestor_of', through_model = BTOAncestorsDeferred)

    _table_name = 'bto'


    @property
    def ancestors(self):
        Q = BTOAncestor.select(BTOAncestor.bto == self.id)
        ancestors = []
        for ancestor in Q:
            ancestors.append(ancestor)
        return ancestors

    def add_ancestor(self, ancestor):
        BTOAncestor.create(bto = self, ancestor = ancestor)

    def remove_ancestor(self, ancestor):
        Q = BTOAncestor.delete().where(BTOAncestor.bto == self.id, BTOAncestor.ancestor == ancestor.id)
        Q.execute()


    #Setters
    def set_bto_id(self, id):
        self.bto_id = id

    def set_label(self, label_):
        self.label = label_ 

    def __get_ancestors_query(self):
        vals = []
        for i in range(0,len(self.data['ancestors'])):
            if (self.data['ancestors'][i] != self.bto_id):
                val = {'bto': self.id, 'ancestor': BTO.get(BTO.bto_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return vals

    def set_ancestors(self):
        vals = []
        for i in range(0,len(self.data['ancestors'])):
            if (self.data['ancestors'][i] != self.bto_id):
                val = {'bto': self.id, 'ancestor': BTO.get(BTO.bto_id == self.data['ancestors'][i]).id }
                vals.append(val)
            #an = BTO.get(BTO.bto_id == self.data['ancestors'][i])
            #self.ancestors =  ManyToManyField(BTO, backref='is_ancestor_of', through_model = BTOAncestorsDeferred)
        BTOAncestor.insert_many(vals).execute()

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

    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        BTOAncestor.create_table()

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        BTOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    #create bto
    @classmethod
    def create_bto(cls, input_db_dir, **files):
        list_bto = Onto.parse_bto_from_json(input_db_dir, files['bto_json_data'])
        btos = [cls(data = dict_) for dict_ in list_bto]
        cls.insert_bto_id(btos,"id")
        cls.insert_label(btos, "label")
        #cls.def_ancestors(btos)
        Controller.save_all()
        #for bt in btos:
        #    bt.set_ancestors()

        vals = []
        for bt in btos:
            val = bt.__get_ancestors_query()
            if len(val) != 0:
                for v in val:
                    vals.append(v)
        for i in range(0, 10):
            print(vals[i])
        BTOAncestor.insert_many(vals).execute()
        return(list_bto)
  
    class Meta():
        table_name = 'bto'

class BTOAncestor(PWModel):
    bto = ForeignKeyField(BTO)
    ancestor = ForeignKeyField(BTO)
    class Meta:
        table_name = 'bto_ancestors'
        database = DbManager.db
        indexes = (
            (('bto', 'ancestor'), True),
        )