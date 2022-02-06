# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import BadRequestException, JSONField
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField, FloatField

from ..base.simple_base_model import SimpleBaseModel
from ..db.db_manager import DbManager
from .reaction_position_data import REACTION_POSITION_DATA


class ReactionPosition:
    rhea_id = None
    x: float = None
    y: float = None
    z: float = None
    points: dict = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.points is None:
            self.points = {}

    @classmethod
    def get_by_rhea_id(cls, rhea_id: str):
        pos = REACTION_POSITION_DATA.get(rhea_id)
        if pos:
            rxn_pos = ReactionPosition()
            rxn_pos.rhea_id = rhea_id
            rxn_pos.x = pos["x"] * 15
            rxn_pos.y = pos["y"] * -15
            rxn_pos.z = None
            rxn_pos.points = pos["points"]
            return rxn_pos
        else:
            return ReactionPosition()

# class ReactionPosition(SimpleBaseModel):
#     rhea_id = CharField(null=True, index=True)
#     x = FloatField(null=True, index=True)
#     y = FloatField(null=True, index=True)
#     z = FloatField(null=True, index=True)
#     points = JSONField(null=True, index=False)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.points is None:
#             self.points = {}

#     @classmethod
#     def get_by_rhea_id(cls, rhea_id: str):
#         pos = REACTION_POSITION_DATA.get(rhea_id)
#         if pos:
#             rxn_pos = ReactionPosition(
#                 rhea_id=rhea_id,
#                 x=pos["x"] * 15,
#                 y=pos["y"] * -15,
#                 z=None,
#                 points=pos["points"],
#             )
#             return rxn_pos
#         else:
#             return ReactionPosition()

#     class Meta:
#         table_name = 'biota_reaction_position'
#         database = DbManager.db
