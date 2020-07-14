
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, Resource
from gws.prism.controller import Controller
from taxo.taxonomy import Taxo
from peewee import CharField, ForeignKeyField

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
    
    def set_ancestor(self, save=True):
        if('ancestor' in self.data.keys()):
            try: 
                parent = Taxonomy.get(Taxonomy.tax_id == self.data['ancestor'])
                #print(Taxonomy.get(Taxonomy.tax_id == self.data['ancestor']))
                self.ancestor = parent
            except:
                print("could not find the parent of: " + str(self.data['tax_id']))
        if save:
            self.save()     

    #Inserts
    @classmethod
    def insert_tax_id(cls, list__, key):
        for tax in list__:
            tax.set_tax_id(tax.data[key])

    @classmethod
    def insert_name(cls, list__, key):
        for tax in list__:
            tax.set_name(tax.data[key])

    @classmethod
    def insert_rank(cls, list__, key):
        for tax in list__:
            tax.set_rank(tax.data[key])
    
    @classmethod
    def insert_ancestor(cls, list__, key):
        for tax in list__:
            tax.set_ancestor(tax.data[key], save=False)
        cls.save_all()

    #Creation
    @classmethod
    def create_taxons_from_list(cls, organism):
        list_taxons = Taxo.parse_taxonomy_from_ncbi(organism)
        taxons = [cls(data = d) for d in list_taxons]
        cls.insert_tax_id(taxons, 'tax_id')
        cls.insert_name(taxons, 'name')
        cls.insert_rank(taxons, 'rank')
        cls.save_all()

        cls.__set_taxons_ancestors(taxons)
        cls.save_all()
        return(list_taxons)

    @classmethod
    def create_taxons_from_dict(cls, list_superkingdom):
        for superkingdom in list_superkingdom:
            dict_taxons = Taxo.get_all_taxonomy(superkingdom)
            taxons = [cls(data = dict_taxons[d]) for d in dict_taxons]
            cls.insert_tax_id(taxons, 'tax_id')
            cls.insert_name(taxons, 'name')
            cls.insert_rank(taxons, 'rank')
            cls.save_all()

            cls.__set_taxons_ancestors(taxons)
            cls.save_all()
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