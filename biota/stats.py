# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from .base import Base
from .bto import BTO
from .eco import ECO
from .sbo import SBO
from .taxonomy import Taxonomy
from .enzyme import Enzyme, Enzo
from .reaction import Reaction
from .compound import Compound
from .protein import Protein

from gws.resource import Resource

class Stats(Resource):
    _table_name = 'gws_biota_stats'

    @classmethod
    def get_stats(cls, renew = False):

        def _renew():
            stats = Stats()
            if len(stats.data) == 0:
                stats.data = {
                    "taxonomy": Taxonomy.select().count(),
                    "compound": Compound.select().count(),
                    "reaction": Reaction.select().count(),
                    "enzo": Enzo.select().count(),
                    "enzyme": Enzyme.select().count(),
                    "protein": Protein.select().count(),
                    "eco": ECO.select().count(),
                    "bto": BTO.select().count(),
                    "sbo": SBO.select().count(),
                }
            stats.save()
            return stats

        if renew:
            stats = _renew()
        else:
            try:
                stats = Stats.select().order_by(Stats.id.desc()).get()
            except:
                stats = _renew()
 
        return stats