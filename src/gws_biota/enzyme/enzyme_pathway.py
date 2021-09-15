# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField

from gws_core.model.typing_register_decorator import typing_registrator
from ..base.base import Base

@typing_registrator(unique_name="EnzymePathway", object_type="MODEL", hide=True)
class EnzymePathway(Base):
    """
    This class represents enzyme def pathpathway.
    """

    ec_number = CharField(null=True, index=True)
    _table_name = 'biota_enzyme_pathway'
