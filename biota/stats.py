# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from biota.base import Base
from biota.bto import BTO
from biota.eco import ECO
from biota.sbo import SBO
from biota.taxonomy import Taxonomy
from biota.enzyme import Enzyme, Enzo
from biota.reaction import Reaction
from biota.compound import Compound
from biota.protein import Protein

from gws.model import Resource

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