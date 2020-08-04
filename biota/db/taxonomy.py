# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, Resource

from biota.db.ontology import Ontology

class Taxonomy(Ontology):
    """
    This class represents the NCBI taxonomy terms.

    The NCBI Taxonomy Database is a curated classification and nomenclature for 
    all of the organisms in the public sequence databases. NCBI Website and Data Usage 
    Policies and Disclaimers (https://www.ncbi.nlm.nih.gov/home/about/policies/).

    :property tax_id: taxonomy id in the ncbi taxonomy
    :type tax_id: CharField
    :property name: scientic name in the ncbi taxonomy
    :type name: CharField
    :property rank: bioologic rank 
    :type rank: CharField
    :property division: the biological division (Bacteria, Eukaryota, Viruses, etc..)
    :type division: CharField
    :property ancestor: parentin the ncbi taxonomy
    :type ancestor: Taxonomy
    """
    
    tax_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    rank = CharField(null=True, index=True)
    division = CharField(null=True, index=True)
    ancestor = ForeignKeyField('self', backref='ancestor', null = True)
    _table_name = 'taxonomy'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # -- C --
    
    @classmethod
    def create_taxonomy_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `taxonomy` database

        :param biodata_db_dir: path to the folder that contain ncbi taxonomy dump files
        :type biodata_db_dir: str
        :param files_test: dictionnary that contains all data files names
        :type files_test: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.ncbi import Taxonomy as NCBITaxonomyHelper

        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(biodata_db_dir, **files)
        dict_taxons = NCBITaxonomyHelper.get_all_taxonomy(biodata_db_dir, dict_ncbi_names, **files)

        bulk_size = 750
        start = 0
        stop = start+bulk_size

        dict_keys = list(dict_taxons.keys())
        
        while True:
            
            #start_time = time.time()

            #step 2
            taxa = [cls(data = dict_taxons[d]) for d in dict_keys[start:stop]]
            
            if len(taxa) == 0:
                break

            #step 3
            for tax in taxa:
                tax.tax_id = tax.data['tax_id']
                if ('name' in tax.data.keys()):
                    tax.name = tax.data['name']
                else:
                    tax.name = "Unspecified"
                tax.rank = tax.data['rank']
                tax.division = tax.data['division']

            #elapsed_time = time.time() - start_time

            cls.save_all(taxa)

            start = stop-1
            stop = start+bulk_size

            #print("Save {} taxa in {} sec".format(bulk_size, elapsed_time))

        #step 4
        page_number = 1
        nb_items_per_page = 750
        while True:
            taxa = Taxonomy.select().paginate(page_number, nb_items_per_page)
            if len(taxa) == 0:
                break
            cls.__set_taxa_ancestors(taxa)
            cls.save_all(taxa)
            page_number = page_number + 1

    # -- S --

    def set_tax_id(self, tax_id):
        """
        Sets the ncbi taxonomy id

        :param tax_id: The ncbi taxonomy id
        :type tax_id: str
        """
        self.tax_id = tax_id
    
    def set_name(self, name):
        """
        Sets the name of the taxonomy

        :param name: The name
        :type name: str
        """
        self.name = name

    def set_rank(self, rank):
        """
        Sets the rank of the taxonomy

        :param rank: The rank
        :type rank: str
        """
        self.rank = rank

    @classmethod
    def __set_taxa_ancestors(cls, taxon_list):
        """
        Create the relationships between the taxonomy entity and his parent in the ncbi taxonomy

        :type list_taxons:
        :parameter list_taxons: list of all taxonomy in the table 
        :returns: None
        """

        tax_dict = {} 
        for tax in taxon_list:
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

    Controller.register_model_classes([Taxonomy])