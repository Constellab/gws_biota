# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField, ForeignKeyField, ModelSelect, TextField
from playhouse.mysql_ext import Match

from ..base.base_ft import BaseFT
from .enzyme_pathway import EnzymePathway
from .deprecated_enzyme import DeprecatedEnzyme


@typing_registrator(unique_name="EnzymeOrtholog", object_type="MODEL", hide=True)
class EnzymeOrtholog(BaseFT):
    """
    This class represents enzyme ortholog.
    """

    ec_number = CharField(null=True, index=True, unique=True)
    pathway = ForeignKeyField(EnzymePathway, backref="enzos", null=True)

    _table_name = "biota_enzo"

    # -- E --

    @property
    def enzymes(self, tax_id: str = None, tax_name: str = None, limit=None):
        from .enzyme import Enzyme

        Q = Enzyme.select().where(Enzyme.ec_number == self.ec_number)
        if not tax_id is None:
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
