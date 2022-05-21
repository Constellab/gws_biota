# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, TextField, ModelSelect
from playhouse.mysql_ext import Match

from gws_core.model.typing_register_decorator import typing_registrator
from ..base.base import Base

@typing_registrator(unique_name="Network", object_type="MODEL", hide=True)
class BiomassReaction(Base):
    """
    This class represents metabolic reactions extracted from Rhea database.

    Rhea is an expert curated resource of biochemical reactions designed for the
    annotation of enzymes and genome-scale metabolic networks and models (https://www.rhea-db.org/).
    Rhea data are available under the Creative
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    :property biorxn_id: the biomass reaction id
    :type biorxn_id: str
    """

    biomass_rxn_id = CharField(null=True, index=True)
    ft_names = CharField(null=True, index=False)
    _table_name = 'biota_biomass_reaction'

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['ft_names'], 'I_F_BIOTA_BIOMASSRXN')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.ft_names), phrase, modifier=modifier))