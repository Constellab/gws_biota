# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import re
from Bio import SeqIO

from gws_core import transaction
from ..base.base import Base
from .protein import Protein
from ..base.base_service import BaseService

class ProteinService(BaseService):

    @classmethod
    @transaction()
    def create_protein_db(cls, biodata_dir = None, **kwargs):
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
                proteins.append(prot)
                if len(proteins) >= 500:
                    Protein.save_all(proteins)
                    proteins = []
            if len(proteins) > 0:
                Protein.save_all(proteins)
                proteins = []
