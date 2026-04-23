

from gws_core import Logger
from peewee import chunked

from .._helper.ncbi import Taxonomy as NCBITaxonomyHelper
from ..base.base_service import BaseService
from .taxonomy import Taxonomy


class TaxonomyService(BaseService):

    @classmethod
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

        # Drop FULLTEXT indexes before bulk insert for much faster insertion.
        # MariaDB rebuilding FULLTEXT indexes incrementally on 2M+ rows is extremely slow.
        # We recreate them in one bulk operation after all data is inserted.
        Logger.info("Dropping FULLTEXT indexes before bulk insert...")
        try:
            Taxonomy.execute_sql("ALTER TABLE biota_taxonomy DROP INDEX ft_names")
            Logger.info("✓ Dropped FULLTEXT index: ft_names")
        except Exception as e:
            Logger.warning(f"Could not drop ft_names index (may not exist): {e}")
        try:
            Taxonomy.execute_sql("ALTER TABLE biota_taxonomy DROP INDEX name")
            Logger.info("✓ Dropped FULLTEXT index: name")
        except Exception as e:
            Logger.warning(f"Could not drop name index (may not exist): {e}")

        for chunk in chunked(dict_taxons.values(), cls.BATCH_SIZE):
            taxa = []
            for data in chunk:
                tax = Taxonomy()
                tax.tax_id = data['tax_id']
                tax.set_name(data.get('name', 'Unspecified'))
                tax.rank = data['rank']
                tax.division = data['division']
                tax.ancestor_tax_id = data['ancestor']
                tax.ft_names = cls.format_ft_names(
                    ["TAX" + data['tax_id'], data.get('name', '')])
                taxa.append(tax)
            Taxonomy.create_all(taxa, use_transaction=False)
        taxa = []

        # Recreate FULLTEXT indexes now that all data is loaded (bulk build = much faster)
        Logger.info("Recreating FULLTEXT indexes after bulk insert...")
        Taxonomy.execute_sql("CREATE FULLTEXT INDEX ft_names ON biota_taxonomy(ft_names)")
        Logger.info("✓ Recreated FULLTEXT index: ft_names")
        Taxonomy.execute_sql("CREATE FULLTEXT INDEX name ON biota_taxonomy(name)")
        Logger.info("✓ Recreated FULLTEXT index: name")

        Logger.info(f"✓ Successfully saved {taxa_count} taxa to database")
