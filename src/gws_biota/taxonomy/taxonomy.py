

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField

from ..ontology.ontology import Ontology


@typing_registrator(unique_name="Taxonomy", object_type="MODEL", hide=True)
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
    name = CharField(null=True, index=True)
    ancestor_tax_id = CharField(null=True, index=True)
    _tax_tree = ['superkingdom', 'clade', 'kingdom', 'subkingdom', 'class',
                 'phylum', 'subphylum', 'order', 'genus', 'family', 'species']
    _table_name = 'biota_taxonomy'
    _children = None
    _siblings = None
    _ancestor = None
    _ancestor_checked = False
    _ancestors = None

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
        return self._ancestors

    # -- C --

    @property
    def children(self):
        if not self._children is None:
            return self._children
        self._children = Taxonomy.select().where(Taxonomy.ancestor_tax_id == self.tax_id)
        return self._children

    # -- G --

    @classmethod
    def get_tax_tree(cls):
        return cls._tax_tree

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
