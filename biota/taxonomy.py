import sys
import os

from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, Resource
from gws.prism.controller import Controller
from biota.helper.taxonomy import Taxo
from peewee import CharField, ForeignKeyField
#import time

####################################################################################
#
# Taxonomy class
#
####################################################################################
class Taxonomy(Resource):
    tax_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    rank = CharField(null=True, index=True)
    division = CharField(null=True, index=True)
    ancestor = ForeignKeyField('self', backref='is_child_of', null = True)
    _table_name = 'taxonomy'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # -- C --
    
    @classmethod
    def create_taxons(cls, path, bulk_size, **files):
        dict_ncbi_names = Taxo.get_ncbi_names(path, **files)
        dict_taxons = Taxo.get_all_taxonomy(path, dict_ncbi_names, **files)

        bulk_size = 750
        start = 0
        stop = start+bulk_size

        dict_keys = list(dict_taxons.keys())
        
        while True:
            
            #start_time = time.time()

            #step 2
            taxons = [cls(data = dict_taxons[d]) for d in dict_keys[start:stop]]
            
            if len(taxons) == 0:
                break

            #step 3
            for tax in taxons:
                tax.tax_id = tax.data['tax_id']
                if ('name' in tax.data.keys()):
                    tax.name = tax.data['name']
                else:
                    tax.name = "Unspecified"
                tax.rank = tax.data['rank']
                tax.division = tax.data['division']

            #elapsed_time = time.time() - start_time

            cls.save_all(taxons)

            start = stop-1
            stop = start+bulk_size

            #print("Save {} taxa in {} sec".format(bulk_size, elapsed_time))

        #step 4
        cls._set_taxons_ancestors(Taxonomy.select())
        cls.save_all()

    # -- S --

    def set_tax_id(self, tax_id__):
        self.tax_id = tax_id__
    
    def set_name(self, name__):
        self.name = name__

    def set_rank(self, rank__):
        self.rank = rank__

    @classmethod
    def _set_taxons_ancestors(cls, list_taxons):
        tax_dict = {} 
        for tax in list_taxons:
            if 'ancestor' in tax.data.keys():
                if int(tax.data['ancestor']) in tax_dict.keys():
                    tax_dict[ int(tax.data['ancestor']) ].append(tax)
                else:
                    tax_dict[ int(tax.data['ancestor']) ] = [ tax ]

        start = 0
        stop = 0
        bluk_size = 750
        tax_ids = list(tax_dict.keys())
        while True:
            if start >= len(tax_ids)-1:
                break

            stop = start+bluk_size
            elems = tax_ids[start:stop]

            q_ancestors = Taxonomy.select().where(Taxonomy.tax_id << elems)

            for parent in q_ancestors:
                for t in tax_dict[ int(parent.tax_id) ]:
                    t.ancestor = parent
            
            start = stop-1

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