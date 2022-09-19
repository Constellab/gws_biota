# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Logger, transaction
from peewee import chunked

from .._helper.ncbi import Taxonomy as NCBITaxonomyHelper
from ..base.base_service import BaseService
from .taxonomy import Taxonomy


class TaxonomyService(BaseService):

    @classmethod
    @transaction()
    def create_taxonomy_db(cls, biodata_dir=None, **kwargs):
        """
        Creates and fills the `taxonomy` database

        :param biodata_dir: path to the folder that contain ncbi taxonomy dump files
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """

        Logger.info("Loading ncbi taxonomy file ...")
        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(biodata_dir, **kwargs)
        dict_taxons = NCBITaxonomyHelper.get_all_taxonomy(biodata_dir, dict_ncbi_names, **kwargs)

        taxa_count = len(dict_taxons)
        Logger.info(f"Saving {taxa_count} taxa ...")
        i = 0
        for chunk in chunked(dict_taxons.values(), cls.BATCH_SIZE):
            i += 1
            taxa = [Taxonomy(data=data) for data in chunk]
            Logger.info(f"... saving taxa chunk {i}/{int(taxa_count/cls.BATCH_SIZE)+1}")
            for tax in taxa:
                tax.tax_id = tax.data['tax_id']
                tax.set_name(tax.data.get('name', 'Unspecified'))
                tax.rank = tax.data['rank']
                tax.division = tax.data['division']
                tax.ancestor_tax_id = tax.data['ancestor']
                tax.ft_names = cls.format_ft_names(["TAX"+tax.tax_id, tax.name])
                del tax.data['ancestor']
            Taxonomy.create_all(taxa)
        taxa = []
