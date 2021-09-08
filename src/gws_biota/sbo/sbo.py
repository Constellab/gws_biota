# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PeeweeModel

from ..db.db_manager import DbManager
from ..base.base import Base
from ..ontology.ontology import Ontology

class SBO(Ontology):
    """
    This class represents SBO terms.

    The SBO (Systems Biology Ontology) is a set of controlled, relational vocabularies 
    of terms commonly used in Systems Biology, and in particular in computational modelling.
    It introduce a layer of semantic information into the standard description of a model, 
    or to annotate the results of biochemical experiments in order to facilitate their efficient reuse
    (http://www.ebi.ac.uk/sbo). SBO is under the Artistic License 2.0 (https://opensource.org/licenses/Artistic-2.0)

    :property sbo_id: id of the sbo term
    :type sbo_id: class:`peewee.CharField` 
    :property name: name of the sbo term
    :type name: class:`peewee.CharField` 
    """

    sbo_id = CharField(null=True, index=True)
    _table_name = 'biota_sbo'
    _ancestors = None

    # -- A --

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors

        self._ancestors = []
        Q = SBOAncestor.select().where(SBOAncestor.sbo == self.id)
        for q in Q:
            self._ancestors.append(q.ancestor)
        
        return self._ancestors

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `sbo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        SBOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        """
        Returns the definition of the got term

        :returns: The definition
        :rtype: str
        """
         
        definition = self.data["definition"]
        return ". ".join(i.capitalize() for i in definition.split(". "))

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `sbo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        SBOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S --

    def set_sbo_id(self, sbo_id):
        """
        Sets the sbo id of the sbo term

        :param sbo_id: The sbo id
        :type sbo_id: str
        """
        self.sbo_id = sbo_id

class SBOAncestor(PeeweeModel):
    """
    This class defines the many-to-many relationship between the sbo terms and theirs ancestors

    :property sbo: id of the concerned sbo term
    :type sbo: CharField 
    :property ancestor: ancestor of the concerned sbo term
    :type ancestor: CharField 
    """
    sbo = ForeignKeyField(SBO)
    ancestor = ForeignKeyField(SBO)
    
    class Meta:
        table_name = 'biota_sbo_ancestors'
        database = DbManager.db
        indexes = (
            (('sbo', 'ancestor'), True),
        )
    