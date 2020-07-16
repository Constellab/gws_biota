
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
    
    def set_ancestor(self):
        if 'ancestor' in self.data.keys():
            try: 
                parent = Taxonomy.get(Taxonomy.tax_id == self.data['ancestor'])
                self.ancestor = parent
            except:
                print("could not find the parent of: " + str(self.data['tax_id']))   

    # inserts
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
    
    # @classmethod
    # def insert_ancestor(cls, list__, key):
    #     for tax in list__:
    #         tax.set_ancestor(tax.data[key])
    #     #cls.save_all()

    # create
    # @classmethod
    # def create_taxons_from_list(cls, organism):
    #     list_taxons = Taxo.parse_taxonomy_from_ncbi(organism)
    #     taxons = [cls(data = d) for d in list_taxons]
    #     cls.insert_tax_id(taxons, 'tax_id')
    #     cls.insert_name(taxons, 'name')
    #     cls.insert_rank(taxons, 'rank')
    #     cls.save_all()

    #     cls.__set_taxons_ancestors(taxons)
    #     cls.save_all()
    #     return(list_taxons)

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
        
        cls.insert_tax_id(taxons, 'tax_id')
        cls.insert_name(taxons, 'name')
        cls.insert_rank(taxons, 'rank')
        cls.save_all()

        elapsed_time = time.time() - start_time
        print("step 3: time = {}".format(elapsed_time/60))

        start_time = time.time()
        cls.__set_taxons_ancestors2(taxons)
        cls.save_all()

        elapsed_time = time.time() - start_time
        print("step 4: time = {}".format(elapsed_time/60))

        print('The superkingdom ' + tax + ' has been correctly loaded')
    
        return(dict_taxons)
    
    # @classmethod
    # def create_taxons_from_dict_at_level(cls, list_superkingdom):
    #     import time

    #     for superkingdom in list_superkingdom:  
    #         start_time = time.time()          
    #         #dict_taxons = Taxo.get_all_taxonomy(superkingdom)

    #         dict_taxons = Taxo.get_taxonomy_lineage(superkingdom, rank_limit = None)

    #         elapsed_time = time.time() - start_time
    #         print("step 1: time = {}, #taxon = {}".format(elapsed_time/60, len(dict_taxons)))
            
    #         start_time = time.time()
    #         taxons = [cls(data = dict_taxons[d]) for d in dict_taxons]

    #         elapsed_time = time.time() - start_time
    #         print("step 2: time = {}".format(elapsed_time/60))
            
    #         cls.insert_tax_id(taxons, 'tax_id')
    #         cls.insert_name(taxons, 'name')
    #         cls.insert_rank(taxons, 'rank')
    #         cls.save_all()

    #         elapsed_time = time.time() - start_time
    #         print("step 3: time = {}".format(elapsed_time/60))

    #         start_time = time.time()
    #         cls.__set_taxons_ancestors2(taxons)
    #         cls.save_all()

    #         elapsed_time = time.time() - start_time
    #         print("step 4: time = {}".format(elapsed_time/60))

    #         print('The superkingdom ' + superkingdom + ' has been correctly loaded')
        
        
    #     status = 'ok'
    #     return(status)

    @classmethod
    def __set_taxons_ancestors(cls, list_taxons):
        for tax in list_taxons:
            tax.set_ancestor()

    @classmethod
    def __set_taxons_ancestors2(cls, list_taxons):
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