# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, DecimalField
from gws_core.model.typing_register_decorator import typing_registrator
from gws_core import BadRequestException, JSONField
from ..base.base import Base
from .reaction_position_data import REACTION_POSITION_DATA

@typing_registrator(unique_name="ReactionPosition", object_type="MODEL", hide=True)
class ReactionPosition(Base):
    rhea_id = CharField(null=True, index=True)
    x = DecimalField(null=True, index=True)
    y = DecimalField(null=True, index=True)
    z = DecimalField(null=True, index=True)
    points = JSONField(null=True, index=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.points is None:
            self.points = {}
        
    @classmethod
    def get_by_rhea_id(cls, rhea_id: str):
        pos = REACTION_POSITION_DATA.get(rhea_id)
        if pos:
            rxn_pos = ReactionPosition(
                rhea_id=rhea_id,
                x=pos["x"] * 20,
                y=pos["y"] * 20,
                z=None,
                points=pos["points"],
            )
            return rxn_pos
        else:
            return ReactionPosition()