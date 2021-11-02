# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from gws_core.model.typing_register_decorator import typing_registrator
from ..db.db_manager import DbManager
from ..base.base import Base
from ..base.protected_model import ProtectedModel
from ..ontology.ontology import Ontology

@typing_registrator(unique_name="GO", object_type="MODEL", hide=True)
class GO(Ontology):
    """
    This class represents GO terms.

    The Gene Ontology (GO) is a major bioinformatics initiative to unify
    the representation of gene and gene product attributes across all 
    species (http://geneontology.org/). GO data are available under the Creative 
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
    
    :property go_id: id of the go term
    :type go_id: CharField 
    :property name: name of the go term
    :type name: CharField 
    :property namespace: namespace of the go term
    :type namespace: CharField 
    """
    go_id = CharField(null=True, index=True)
    namespace = CharField(null=True, index=True)
    _table_name = 'biota_go'

    # -- C -- 
    
    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `go` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        GOAncestor.create_table()

    # -- D --

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `go` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        GOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    
    @property
    def definition(self):
        """
        Returns the definition of the got term

        :returns: The definition
        :rtype: str
        """
        return self.data["definition"]

    # -- S --

    def set_definition(self, definition):
        """
        Set the definition of the go term

        :param definition: The definition
        :type definition: str
        """
        self.definition = definition

    def set_go_id(self, id):
        """
        Sets the id of the go term

        :param id: The id
        :type id: str
        """
        self.go_id = id
    
    def set_namespace(self, namespace):
        """
        Sets the namespace of the go term

        :param namespace: The namespace
        :type namespace: str
        """
        self.namespace = namespace


class GOAncestor(ProtectedModel):
    """
    This class defines the many-to-many relationship between the go terms and theirs ancestors

    :property go: id of the go term
    :type go: GO 
    :property ancestor: ancestor of the go term
    :type ancestor: GO 
    """

    go = ForeignKeyField(GO)
    ancestor = ForeignKeyField(GO)
    
    class Meta:
        table_name = 'biota_go_ancestors'
        database = DbManager.db
        indexes = (
            (('go', 'ancestor'), True),
        )
