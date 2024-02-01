# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Logger, transaction, FileDownloader, Settings
from peewee import chunked

from .._helper.ncbi import Taxonomy as NCBITaxonomyHelper
from ..base.base_service import BaseService
from .taxonomy import Taxonomy


class TaxonomyService(BaseService):

    @classmethod
    @transaction()
    def create_taxonomy_db(cls, biodata_dir: str, taxonomy_tar_url: str):
        """
        Creates and fills the `taxonomy` database

        :param biodata_dir: path to the folder that contain ncbi taxonomy dump files
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """
        temp_dir = Settings.get_instance().make_temp_dir()
        file_downloader = FileDownloader(temp_dir)
        taxonomy_dir = file_downloader.download_file_if_missing(
            taxonomy_tar_url, 'taxonomy.tar.gz', decompress_file=True)

        ncbi_nodes = f"{taxonomy}/nodes.dmp"
        ncbi_names = f"{taxonomy}/names.dmp"
        ncbi_division = f"{taxonomy}/division.dmp"

        Logger.info("Loading ncbi taxonomy file ...")
        dict_ncbi_names = NCBITaxonomyHelper.get_ncbi_names(biodata_dir, ncbi_names)
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
