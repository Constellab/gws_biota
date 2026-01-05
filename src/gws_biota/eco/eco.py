

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField, ForeignKeyField

from ..base.protected_base_model import ProtectedBaseModel
from ..ontology.ontology import Ontology


@typing_registrator(unique_name="ECO", object_type="MODEL", hide=True)
class ECO(Ontology):
    """
    This class represents Evidence ECO terms.

    The Evidence and Conclusion Ontology (ECO) contains terms that describe
    types of evidence and assertion methods. ECO terms are used in the process of
    biocuration to capture the evidence that supports biological assertions
    (http://www.evidenceontology.org/). ECO is under the Creative Commons License CC0 1.0 Universal (CC0 1.0),
    https://creativecommons.org/publicdomain/zero/1.0/.

    :property eco_id: id of the eco term
    :type eco_id: class:`peewee.CharField`
    :property name: name of the eco term
    :type name: class:`peewee.CharField`
    """

    eco_id = CharField(null=True, index=True)

    _ancestors = None

    # -- A --

    @property
    def ancestors(self):
        if self._ancestors is not None:
            return self._ancestors
        self._ancestors = []
        query = ECOAncestor.select().where(ECOAncestor.eco == self.id)
        for elt in query:
            self._ancestors.append(elt.ancestor)
        return self._ancestors

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `eco` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        ECOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        """
        return self.definition
        """
        definition = self.data["definition"]
        return ". ".join(i.capitalize() for i in definition.split(". "))

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `eco` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        ECOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S --

    def set_eco_id(self, id):
        """
        set self.eco_id
        """
        self.eco_id = id

    class Meta:
        table_name = 'biota_eco'
        is_table = True


class ECOAncestor(ProtectedBaseModel):
    """
    This class defines the many-to-many relationship between the eco terms and theirs ancestors

    :type eco: CharField
    :property eco: id of the concerned eco term
    :type ancestor: CharField
    :property ancestor: ancestor of the concerned eco term
    """

    eco = ForeignKeyField(ECO)
    ancestor = ForeignKeyField(ECO)

    class Meta:
        table_name = 'biota_eco_ancestors'
        is_table = True
        indexes = (
            (('eco', 'ancestor'), True),
        )
