# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, TextField, IntegerField

from ..base.base import Base
from ..taxonomy.taxonomy import Taxonomy

class Protein(Base):
    """
    This class represents genes
    """

    uniprot_id = TextField(null=True, index=True)
    uniprot_db = CharField(null=False, index=False)       #sp or tr
    uniprot_gene = CharField(null=True, index=True)
    evidence_score = IntegerField(null=True, index=True)  #1, 2, 3, 4, 5
    tax_id = CharField(null=True, index=True)

    _table_name = 'biota_protein'
    _evidence_score_description = {
         0: "No evidence score",
         1: "Experimental evidence at protein level",
         2: "Experimental evidence at transcript level",
         3: "Protein inferred from homology",
         4: "Protein predicted",
         5: "Protein uncertain"
    }

    # -- D --

    @property
    def description(self):
        return self.data['description']

    # -- P --
    @property
    def evidence_score_description(self):
        return self._evidence_score_description[ self.evidence_score ]
    
    # -- S --

    @property
    def sequence(self):
        return self.data['sequence']

    def set_sequence(self, sequence):
        self.data['sequence'] = sequence

    def set_description(self, desc):
        self.data['description'] = desc

    # -- T --
    
    @property
    def taxonomy(self):
        try:
            return Taxonomy.get(Taxonomy.tax_id == self.tax_id)
        except:
            return None
