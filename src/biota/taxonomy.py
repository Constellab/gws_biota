
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

    # setters
    def set_tax_id(self, tax_id__):
        self.tax_id = tax_id__
    
    def set_name(self, name__):
        self.name = name__

    def set_rank(self, rank__):
        self.rank = rank__

    @classmethod
    def create_taxons_from_dict(cls, taxlist):
        for tax in taxlist:
            cls.create_taxons_from_dict_at_level(tax, "phylum")

    @classmethod
    def create_taxons_from_dict_at_level(cls, tax, level):
        print(tax)
        import time

        start_time = time.time()          

        dict_taxons = Taxo.get_taxonomy_lineage(tax, rank_limit = level)

        if len(dict_taxons) == 0:
            return dict_taxons

        elapsed_time = time.time() - start_time
        print("step 1: time = {}, #taxon = {}".format(elapsed_time/60, len(dict_taxons)))
        
        start_time = time.time()
        taxons = [cls(data = dict_taxons[d]) for d in dict_taxons]

        elapsed_time = time.time() - start_time
        print("step 2: time = {}".format(elapsed_time/60))
        
        for tax in dict_taxons:
            tax.tax_id = tax.data['tax_id']
            tax.name = tax.data['name']
            tax.rank = tax.data['rank']

        cls.save_all()

        elapsed_time = time.time() - start_time
        print("step 3: time = {}".format(elapsed_time/60))

        start_time = time.time()
        cls._set_taxons_ancestors(taxons)
        cls.save_all()

        elapsed_time = time.time() - start_time
        print("step 4: time = {}".format(elapsed_time/60))

        print('The superkingdom ' + tax + ' has been correctly loaded')
    
        return(dict_taxons)

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

            stop = min(start+bluk_size, len(list_taxons)-1)
            elems = tax_ids[start:(stop+1)]

            print(len(elems))

            if len(elems) == 0:
                break

            q_ancestors = Taxonomy.select().where(Taxonomy.tax_id << elems)

            for parent in q_ancestors:
                for t in tax_dict[ int(parent.tax_id) ]:
                    t.ancestor = parent
            
            start = stop

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