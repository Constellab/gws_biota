# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, DecimalField
from gws_core.model.typing_register_decorator import typing_registrator
from gws_core import BadRequestException
from ..base.base import Base

from .compound_position_data import COMPOUND_POSITION_DATA

@typing_registrator(unique_name="CompoundPosition", object_type="MODEL", hide=True)
class CompoundPosition(Base):
    chebi_id = CharField(null=True, index=True)
    x = DecimalField(null=True, index=True)
    y = DecimalField(null=True, index=True)
    z = DecimalField(null=True, index=True)

    @classmethod
    def get_by_chebi_id(cls, chebi_id: str):
        pos = COMPOUND_POSITION_DATA.get(chebi_id)
        if pos:
            comp_pos = CompoundPosition(
                chebi_id=chebi_id,
                x=pos["x"] * 20,
                y=pos["y"] * 20,
                z=None
            )
            return comp_pos
        else:
            return CompoundPosition()