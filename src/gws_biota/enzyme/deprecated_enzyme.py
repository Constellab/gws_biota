# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField

from gws_core.model.typing_register_decorator import typing_registrator
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
    _table_name = 'biota_deprecated_enzymes'

    @property
    def reason(self):
        return self.data["reason"]
    
    def select_new_enzymes(self):
        from .enzyme import Enzyme
        Q = {}
        if self.new_ec_number:
            tmp_Q = Enzyme.select().where(Enzyme.ec_number == self.new_ec_number)        
            if tmp_Q:
                for e in tmp_Q:
                    Q[e.id] = e
            else:
                Q = {}
                # if the new enzyme if also deprecated, we follow the deprecation chain
                deprec_Q = DeprecatedEnzyme.select().where(DeprecatedEnzyme.ec_number == self.new_ec_number)
                for deprec in deprec_Q:
                    for e in deprec.select_new_enzymes():
                        Q[e.id] = e
        
        return list(Q.values())
