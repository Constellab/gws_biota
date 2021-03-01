# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import re

from peewee import CharField, TextField, IntegerField
from Bio import SeqIO

from biota.entity import Entity
from biota.taxonomy import Taxonomy as BiotaTaxo

class Protein(Entity):
    """
    This class represents genes
    """

    uniprot_id = TextField(null=True, index=True)
    uniprot_db = CharField(null=False, index=False)       #sp or tr
    uniprot_gene = CharField(null=True, index=True)
    evidence_score = IntegerField(null=True, index=True)  #1, 2, 3, 4, 5
    tax_id = CharField(null=True, index=True)

    _fts_fields = { **Entity._fts_fields, 'description': 1.0 }
    _table_name = 'biota_protein'
    _evidence_score_description = {
         0: "No evidence score",
         1: "Experimental evidence at protein level",
         2: "Experimental evidence at transcript level",
         3: "Protein inferred from homology",
         4: "Protein predicted",
         5: "Protein uncertain"
    }
    
    @classmethod
    def create_protein_db(cls, biodata_dir = None, **kwargs):
        job = kwargs.get('job',None)
        file_path = os.path.join(biodata_dir, kwargs["protein_file"])
        
        with open(file_path, "rU") as handle:
            proteins = []
            for record in SeqIO.parse(handle, "fasta"):
                m = re.match(r".*OX=([0-9]+).*PE=(\d).*", record.description)
                tax = m.group(1) if m else ""
                evidence = int(m.group(2)) if m else 0
    
                prot = Protein(
                    uniprot_id = record.id.split("|")[1],
                    uniprot_db = record[1:2],
                    uniprot_gene = record.id.split("|")[2],
                    evidence_score = evidence,
                    tax_id = tax
                )
    
                prot.set_sequence(str(record.seq))
                prot.set_description(record.description)

                if not job is None:
                    prot._set_job(job)

                proteins.append(prot)

                if len(proteins) >= 500:
                    Protein.save_all(proteins)
                    proteins = []
            
            if len(proteins) > 0:
                cls.save_all(proteins)
                proteins = []

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
            return BiotaTaxo.get(BiotaTaxo.tax_id == self.tax_id)
        except:
            return None
