import sys
import os

from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from taxo.taxonomy import Taxo
from peewee import IntegerField, DateField, DateTimeField, CharField, ForeignKeyField

from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# Taxonomy class
#
####################################################################################
class Taxonomy(Resource):
    tax_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    rank = CharField(null=True, index=True)
    ancestor = ForeignKeyField('self', backref='is_child_of', null = True)
    _table_name = 'taxonomy'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #Setters
    def set_tax_id(self, tax_id__):
        self.tax_id = tax_id__
    
    def set_name(self, name__):
        self.name = name__

    def set_rank(self, rank__):
        self.rank = rank__
    
    def set_ancestor(self):
        if('ancestor' in self.data.keys()):
            try: 
                parent = Taxonomy.get(Taxonomy.tax_id == self.data['ancestor'])
                #print(Taxonomy.get(Taxonomy.tax_id == self.data['ancestor']))
                self.ancestor = parent
            except:
                print("could not find the parent of: " + str(self.data['tax_id']))
        self.save()     

    #Inserts
    def insert_tax_id(list__, key):
        for tax in list__:
            tax.set_tax_id(tax.data[key])

    def insert_name(list__, key):
        for tax in list__:
            tax.set_name(tax.data[key])

    def insert_rank(list__, key):
        for tax in list__:
            tax.set_rank(tax.data[key])
    
    def insert_ancestor(list__, key):
        for tax in list__:
            tax.set_ancestor(tax.data[key])

    #Creation
    @classmethod
    def create_taxons_from_list(cls, organism):
        list_taxons = Taxo.parse_taxonomy_from_ncbi(organism)
        taxons = [cls(data = d) for d in list_taxons]
        cls.insert_tax_id(taxons, 'tax_id')
        cls.insert_name(taxons, 'name')
        cls.insert_rank(taxons, 'rank')
        Controller.save_all()
        cls.__set_taxons_ancestors(taxons)
        return(list_taxons)

    @classmethod
    def create_taxons_from_dict(cls, list_superkingdom):
        for superkingdom in list_superkingdom:
            dict_taxons = Taxo.get_all_taxonomy(superkingdom)
            taxons = [cls(data = dict_taxons[d]) for d in dict_taxons]
            cls.insert_tax_id(taxons, 'tax_id')
            cls.insert_name(taxons, 'name')
            cls.insert_rank(taxons, 'rank')
            Controller.save_all()
            cls.__set_taxons_ancestors(taxons)
            Controller.save_all()
            print('The superkingdom ' + superkingdom + ' has been correctly loaded')
        status = 'ok'
        return(status)
    
    @classmethod
    def __set_taxons_ancestors(cls, list_taxons):
        for tax in list_taxons:
            tax.set_ancestor()

    class Meta():
        table_name = 'taxonomy'

class TaxonomyJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.tax_id}},
            "name": {{view_model.model.name}},
            }
        """)

class TaxonomyJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.tax_id}},
            "name": {{view_model.model.name}},
            "rank": {{view_model.model.rank}},
            "ancestor": {{view_model.model.ancestor.tax_id}},
            }
        """)