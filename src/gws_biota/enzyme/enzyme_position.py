# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, FloatField
from gws_core.model.typing_register_decorator import typing_registrator
from gws_core import BadRequestException
from ..base.base import Base

@typing_registrator(unique_name="EnzymePosition", object_type="MODEL", hide=True)
class EnzymePosition(Base):
    ec_number = CharField(null=True, index=True)
    x_position = FloatField(null=True, index=True)
    y_position = FloatField(null=True, index=True)
    z_position = FloatField(null=True, index=True)