

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField

from ..base.base import Base


@typing_registrator(unique_name="DeprecatedEnzyme", object_type="MODEL", hide=True)
class DeprecatedEnzyme(Base):
    """
    This class represents depreacted EC numbers of enzymes.
    A deprecated enzyme is an enzyme of which the EC number has changed at least once.
    The old EC number is therefore tagged as deprecated and is not valid anymore.

    :property ec_number: The deprecated ec number
    :type ec_number: str
    :property new_ec_number: The new ec number
    :type new_ec_number: str
    """

    ec_number = CharField(null=True, index=True)
    new_ec_number = CharField(null=True, index=True)

    @property
    def reason(self):
        return self.data.get("reason", "")

    def select_new_enzymes(self, select_only_one=False):
        from .enzyme import Enzyme
        query = []
        if self.new_ec_number:
            query = Enzyme.select().where(Enzyme.ec_number == self.new_ec_number)
            if select_only_one:
                query = query.limit(1)
        return query

    class Meta:
        table_name = 'biota_deprecated_enzymes'
        is_table = True
