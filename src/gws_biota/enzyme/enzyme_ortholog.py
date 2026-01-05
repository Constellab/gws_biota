

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField, ForeignKeyField

from ..base.base_ft import BaseFT
from .deprecated_enzyme import DeprecatedEnzyme
from .enzyme_pathway import EnzymePathway


@typing_registrator(unique_name="EnzymeOrtholog", object_type="MODEL", hide=True)
class EnzymeOrtholog(BaseFT):
    """
    This class represents enzyme ortholog.
    """

    ec_number = CharField(null=True, index=True, unique=True)
    pathway = ForeignKeyField(EnzymePathway, backref="enzos", null=True)

  # -- E --

    @property
    def enzymes(self, tax_id: str = None, tax_name: str = None, limit=None):
        from .enzyme import Enzyme

        Q = Enzyme.select().where(Enzyme.ec_number == self.ec_number)
        if tax_id is not None:
            Q = Q.where(Enzyme.tax_id == tax_id)
        if limit:
            Q = Q.limit(limit)
        return Q.order_by(Enzyme.data["RN"].desc())

    # -- N --

    @property
    def synomyms(self):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme orthologue
        :rtype: str
        """

        return ",".join([sn.capitalize() for sn in self.data.get("SN", [""])])

    @property
    def related_deprecated_enzyme(self):
        """ Returns depreacated enzymes related to this enzyme """
        return DeprecatedEnzyme.get_or_none(DeprecatedEnzyme.new_ec_number == self.ec_number)

    class Meta:
        table_name = 'biota_enzo'
        is_table = True
