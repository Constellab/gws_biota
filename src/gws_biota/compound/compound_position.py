# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import random
from typing import List, Union

from gws_core import BadRequestException
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import BooleanField, CharField, FloatField

from ..base.simple_base_model import SimpleBaseModel
from ..db.db_manager import DbManager
from ._layout.layout import Layout
from ._position.all import *

COMPOUND_POSITION_DATA = Layout.generate()


class CompoundPosition:
    chebi_id: str = None
    x: float = None
    y: float = None
    z: float = None
    is_major: bool = None
    _position_data: dict = None
    _compartment_offset = {}

    FACTOR = 10

    @classmethod
    def get_position_data(cls):
        if cls._position_data is None:
            cls._position_data = {}
            for key, val in COMPOUND_POSITION_DATA.items():
                pos = {
                    "x": val["x"],
                    "y": val["y"],
                    "is_major": val.get("is_major", False)
                }
                cls._position_data[key] = pos
                alt = val.get("alt", [])
                for alt_key in alt:
                    cls._position_data[alt_key] = pos
        return cls._position_data

    @classmethod
    def get_by_chebi_id(cls, chebi_ids: Union[str, List[str]], compartment=None):
        def rnd_offset():
            rnd_num = random.uniform(0, 1)
            return 10 if rnd_num >= 0.5 else -10

        if isinstance(chebi_ids, str):
            pos = cls.get_position_data().get(chebi_ids)
        else:
            for c_id in chebi_ids:
                pos = cls.get_position_data().get(c_id)
                chebi_id = c_id
                if pos:
                    break

        if pos:
            comp_pos = CompoundPosition()
            comp_pos.chebi_id = chebi_id
            if pos.get("x") is not None:
                comp_pos.x = pos["x"] * cls.FACTOR
            else:
                comp_pos.x = None
            if pos.get("y") is not None:
                comp_pos.y = -pos["y"] * cls.FACTOR
            else:
                comp_pos.y = None
            comp_pos.z = None
            comp_pos.is_major = pos["is_major"]

            # add offset of compartment
            if compartment == "e":
                comp_pos.x += rnd_offset() * cls.FACTOR
                comp_pos.y += rnd_offset() * cls.FACTOR
            elif compartment != "c":
                comp_pos.x += rnd_offset() * cls.FACTOR
                comp_pos.y += rnd_offset() * cls.FACTOR

            return comp_pos

        else:
            return CompoundPosition()

# class CompoundPosition(SimpleBaseModel):
#     chebi_id = CharField(null=True, index=True)
#     x = FloatField(null=True, index=True)
#     y = FloatField(null=True, index=True)
#     z = FloatField(null=True, index=True)
#     is_major = BooleanField(null=True, index=True)

#     _position_data: dict = {}

#     @classmethod
#     def get_position_data(cls):
#         if not cls._position_data:
#             cls._position_data = {}
#             for key, val in COMPOUND_POSITION_DATA.items():
#                 pos = {"x": val["x"], "y": val["y"]}
#                 cls._position_data[key] = pos
#                 alt = val.get("alt", [])
#                 for alt_key in alt:
#                     cls._position_data[alt_key] = pos
#         return cls._position_data

#     @classmethod
#     def get_by_chebi_id(cls, chebi_id: str):
#         pos = cls.get_position_data().get(chebi_id)
#         if pos:
#             comp_pos = CompoundPosition(
#                 chebi_id=chebi_id,
#                 x=pos["x"] * 15,
#                 y=pos["y"] * -15,
#                 z=None
#             )
#             return comp_pos
#         else:
#             return CompoundPosition()

#     class Meta:
#         table_name = 'biota_compound_position'
#         database = DbManager.db
