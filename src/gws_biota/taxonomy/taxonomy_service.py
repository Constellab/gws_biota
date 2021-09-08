# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction
from .._helper.ncbi import Taxonomy as NCBITaxonomyHelper
from .taxonomy import Taxonomy

class TaxonomyService:
    
    @classmethod
    @transaction()
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

        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(biodata_dir, **kwargs)
        dict_taxons = NCBITaxonomyHelper.get_all_taxonomy(biodata_dir, dict_ncbi_names, **kwargs)
        bulk_size = 750
        start = 0
        stop = start+bulk_size
        dict_keys = list(dict_taxons.keys())
        while True:
            #step 2
            taxa = [Taxonomy(data = dict_taxons[d]) for d in dict_keys[start:stop]]
            if len(taxa) == 0:
                break
            #step 3
            for tax in taxa:
                tax.tax_id = tax.data['tax_id']
                if 'name' in tax.data.keys():
                    tax.set_name(tax.data['name'])
                else:
                    tax.set_name("Unspecified")
                tax.rank = tax.data['rank']
                tax.division = tax.data['division']
                tax.ancestor_tax_id = tax.data['ancestor']
                del tax.data['ancestor']
            Taxonomy.save_all(taxa)
            start = stop
            stop = start+bulk_size
