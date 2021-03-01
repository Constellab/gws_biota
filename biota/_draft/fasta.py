# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import re

from peewee import CharField, TextField
from Bio import SeqIO

from biota.db.entity import Entity
from biota.db.taxonomy import Taxonomy as BiotaTaxo

class Fasta(Entity):
    """
    This class represents genes
    """

    uniprot_id = TextField(null=True, index=True)
    uniprot_gene = CharField(null=True, index=True)
    tax_id = CharField(null=True, index=True)

    _fts_fields = { **Entity._fts_fields, 'description': 1.0 }
    _table_name = 'fasta'

    @classmethod
    def create_fasta_db(cls, biodata_dir = None, **kwargs):
        job = kwargs.get('job',None)
        file_path = os.path.join(biodata_dir, kwargs["fasta_file"])
        
        with open(file_path, "rU") as handle:
            fas = []
            for record in SeqIO.parse(handle, "fasta"):
                m = re.match(r".*OX=([0-9]+).*", record.description)
                if m:
                    tax = m.group(1)
                else:
                    tax = ""

                fa = Fasta(
                    uniprot_id = record.id.split("|")[1],
                    uniprot_gene = record.id.split("|")[2],
                    tax_id = tax
                )
                fa.set_sequence(str(record.seq))
                fa.set_description(record.description)

                if not job is None:
                    fa._set_job(job)

                fas.append(fa)

                if len(fas) >= 500:
                    Fasta.save_all(fas)
                    fas = []
            
            if len(fas) > 0:
                cls.save_all(fas)
                fas = []

    # -- D --

    @property
    def description(self):
        return self.data['description']

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
            return BiotaTaxo.get(BiotaTaxo.tax_id == self.tax_id)
        except:
            return None
