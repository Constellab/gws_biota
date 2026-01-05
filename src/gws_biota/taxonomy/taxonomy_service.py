

from gws_core import Logger
from peewee import chunked

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.ncbi import Taxonomy as NCBITaxonomyHelper
from ..base.base_service import BaseService
from .taxonomy import Taxonomy


class TaxonomyService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_taxonomy_db(cls, path, taxdump_files):
        """
        Creates and fills the `taxonomy` database

        :param path: path to the folder that contain ncbi taxonomy dump files
        :type path: str
        :param taxdump_files: url that contains all data files names
        :type taxdump_files: tar.gz url
        :returns: None
        :rtype: None
        """
        ncbi_nodes = f"{taxdump_files}/nodes.dmp"
        ncbi_names = f"{taxdump_files}/names.dmp"
        ncbi_division = f"{taxdump_files}/division.dmp"

        Logger.info("Loading ncbi taxonomy file ...")
        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(ncbi_names)
        dict_taxons = NCBITaxonomyHelper.get_all_taxonomy(
            dict_ncbi_names, ncbi_nodes, ncbi_division)

        taxa_count = len(dict_taxons)
        Logger.info(f"Saving {taxa_count} taxa ...")
        i = 0
        for chunk in chunked(dict_taxons.values(), cls.BATCH_SIZE):
            i += 1
            taxa = [Taxonomy(data=data) for data in chunk]
            Logger.info(
                f"... saving taxa chunk {i}/{int(taxa_count/cls.BATCH_SIZE)+1}")
            for tax in taxa:
                tax.tax_id = tax.data['tax_id']
                tax.set_name(tax.data.get('name', 'Unspecified'))
                tax.rank = tax.data['rank']
                tax.division = tax.data['division']
                tax.ancestor_tax_id = tax.data['ancestor']
                tax.ft_names = cls.format_ft_names(
                    ["TAX"+tax.tax_id, tax.name])
                del tax.data['ancestor']
            Taxonomy.create_all(taxa)
        taxa = []
