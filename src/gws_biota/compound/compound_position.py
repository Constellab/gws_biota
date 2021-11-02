# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, FloatField
from gws_core.model.typing_register_decorator import typing_registrator
from gws_core import BadRequestException

from ..db.db_manager import DbManager
from ..base.protected_model import ProtectedModel
from .compound_position_data import COMPOUND_POSITION_DATA

class CompoundPosition(ProtectedModel):
    chebi_id = CharField(null=True, index=True)
    x = FloatField(null=True, index=True)
    y = FloatField(null=True, index=True)
    z = FloatField(null=True, index=True)

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

    class Meta:
        table_name = 'biota_compound_position'
        database = DbManager.db