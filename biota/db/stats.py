# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from biota.db.base import Base
from biota.db.bto import BTO
from biota.db.eco import ECO
from biota.db.sbo import SBO
from biota.db.po import PO
from biota.db.taxonomy import Taxonomy
from biota.db.enzyme import Enzyme
from biota.db.reaction import Reaction
from biota.db.compound import Compound
from biota.db.fasta import Fasta


class Stats(Base):
    _table_name = 'stats'

    @classmethod
    def get_stats(cls, renew = False):

        def _renew():
            stats = Stats()
            if len(stats.data) == 0:
                stats.data = {
                    "taxonomy": Taxonomy.select().count(),
                    "compound": Compound.select().count(),
                    "reaction": Reaction.select().count(),
                    "enzyme": Enzyme.select().count(),
                    "fasta": Fasta.select().count(),
                    "eco": ECO.select().count(),
                    "bto": BTO.select().count(),
                    "sbo": SBO.select().count(),
                    "po": PO.select().count()
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