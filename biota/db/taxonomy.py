# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from gws.model import Resource
from biota.db.ontology import Ontology

class Taxonomy(Ontology):
    """
    This class represents the NCBI taxonomy terms.

    The NCBI Taxonomy Database is a curated classification and nomenclature for 
    all of the organisms in the public sequence databases. NCBI Website and Data Usage 
    Policies and Disclaimers (https://www.ncbi.nlm.nih.gov/home/about/policies/).

    :property tax_id: taxonomy id in the ncbi taxonomy
    :type tax_id: CharField
    :property rank: bioologic rank 
    :type rank: CharField
    :property division: the biological division (Bacteria, Eukaryota, Viruses, etc..)
    :type division: CharField
    :property ancestor: parentin the ncbi taxonomy
    :type ancestor: Taxonomy
    """
    
    tax_id = CharField(null=True, index=True)
    rank = CharField(null=True, index=True)
    division = CharField(null=True, index=True)
    ancestor_tax_id = CharField(null=True, index=True)
    #ancestor = ForeignKeyField('self', backref='children', null = True)
    
    _fts_fields = { **Ontology._fts_fields }
    _table_name = 'taxonomy'

    _children = None
    _siblings = None
    _ancestor = None
    _ancestor_checked = False
    _ancestors = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # -- A --

    @property
    def ancestor(self):
        if self._ancestor_checked:
            return self._ancestor

        self._ancestor_checked = True
        try:
            if self.tax_id == self.ancestor_tax_id:
                return None
                
            self._ancestor = Taxonomy.get(Taxonomy.tax_id == self.ancestor_tax_id)
            return self._ancestor
        except:
            return None

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors

        tax = self
        self._ancestors = []
        while not tax.ancestor is None: 
            self._ancestors.append(tax.ancestor)
            tax = tax.ancestor

        self._ancestors.reverse()
        return self._ancestors

    # -- C --
    
    @property
    def children(self):
        if not self._children is None:
            return self._children

        self._children = Taxonomy.select().where(Taxonomy.ancestor_tax_id == self.tax_id)
        return self._children

    @classmethod
    def create_taxonomy_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `taxonomy` database

        :param biodata_dir: path to the folder that contain ncbi taxonomy dump files
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.ncbi import Taxonomy as NCBITaxonomyHelper

        job = kwargs.get('job',None)
        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(biodata_dir, **kwargs)
        dict_taxons = NCBITaxonomyHelper.get_all_taxonomy(biodata_dir, dict_ncbi_names, **kwargs)

        bulk_size = 750
        start = 0
        stop = start+bulk_size

        dict_keys = list(dict_taxons.keys())
        
        while True:

            #step 2
            taxa = [cls(data = dict_taxons[d]) for d in dict_keys[start:stop]]
            
            if len(taxa) == 0:
                break

            #step 3
            for tax in taxa:
                tax.tax_id = tax.data['tax_id']
                
                if 'title' in tax.data.keys():
                    tax.set_name(tax.data['title'])
                else:
                    tax.set_name("Unspecified")

                tax.rank = tax.data['rank']
                tax.division = tax.data['division']
                tax.ancestor_tax_id = tax.data['ancestor']

                if not job is None:
                    tax._set_job(job)

                del tax.data['tax_id']
                del tax.data['rank']
                del tax.data['division']
                del tax.data['ancestor']

            cls.save_all(taxa)

            start = stop
            stop = start+bulk_size

        # #step 4
        # page_number = 1
        # nb_items_per_page = 750
        # while True:
        #     taxa = Taxonomy.select().paginate(page_number, nb_items_per_page)
        #     if len(taxa) == 0:
        #         break
        #     cls.__set_taxa_ancestors(taxa)
        #     cls.save_all(taxa)
        #     page_number = page_number + 1
    
    # -- S --

    @property
    def siblings(self):
        if not self._siblings is None:
            return self._siblings

        self._siblings = Taxonomy.select().where(Taxonomy.ancestor_tax_id == self.ancestor_tax_id)
        return self._siblings

    def set_tax_id(self, tax_id):
        """
        Sets the ncbi taxonomy id

        :param tax_id: The ncbi taxonomy id
        :type tax_id: str
        """
        self.tax_id = tax_id

    def set_rank(self, rank):
        """
        Sets the rank of the taxonomy

        :param rank: The rank
        :type rank: str
        """
        self.rank = rank

    # @classmethod
    # def __set_taxa_ancestors(cls, taxon_list):
    #     """
    #     Create the relationships between the taxonomy entity and his parent in the ncbi taxonomy

    #     :type list_taxons:
    #     :parameter list_taxons: list of all taxonomy in the table 
    #     :returns: None
    #     """

    #     tax_dict = {} 
    #     for tax in taxon_list:
    #         if 'ancestor' in tax.data.keys():
    #             if tax.data['ancestor'] in tax_dict.keys():
    #                 tax_dict[ tax.data['ancestor'] ].append(tax)
    #             else:
    #                 tax_dict[ tax.data['ancestor'] ] = [ tax ]

    #     bluk_size = 750
    #     start = 0
    #     stop = start+bluk_size
    #     tax_ids = list(tax_dict.keys())
    #     while True:
    #         if start >= len(tax_ids)-1:
    #             break

    #         elems = tax_ids[start:stop]
    #         q_ancestors = Taxonomy.select().where(Taxonomy.tax_id << elems)

    #         for parent in q_ancestors:
    #             for t in tax_dict[ parent.tax_ids ]:
    #                 t.ancestor = parent
            
    #         start = stop
    #         stop = start+bluk_size