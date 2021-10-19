# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, FloatField
from gws_core.model.typing_register_decorator import typing_registrator
from gws_core import BadRequestException
from ..base.base import Base

@typing_registrator(unique_name="CompoundPosition", object_type="MODEL", hide=True)
class CompoundPosition(Base):
    chebi_id = CharField(null=True, index=True)
    x = FloatField(null=True, index=True)
    y = FloatField(null=True, index=True)
    z = FloatField(null=True, index=True)