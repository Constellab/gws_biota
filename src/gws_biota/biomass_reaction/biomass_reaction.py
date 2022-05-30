# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField

from ..base.base_ft import BaseFT


@typing_registrator(unique_name="Network", object_type="MODEL", hide=True)
class BiomassReaction(BaseFT):
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
    _table_name = 'biota_biomass_reaction'
