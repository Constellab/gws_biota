

import gzip
import re

from Bio import SeqIO
from gws_biota.src.gws_biota.db.biota_db_manager import BiotaDbManager
from gws_core import Logger

from ..base.base_service import BaseService
from .protein import Protein


class ProteinService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_protein_db(cls, path, protein_file):
        """
        Creates and fills the `protein` database

        :param path: path of the file
        :type path: str
        :param protein_file: file that contains data file name
        :type protein_file: file
        :returns: None
        :rtype: None
        """

        Logger.info(f"Loading and saving uniprot data ...")
        with gzip.open(protein_file, "rt") as handle:
            proteins = []
            count = 0
            batch = 0
            for record in SeqIO.parse(handle, "fasta"):
                m = re.match(r".*OX=([0-9]+).*PE=(\d).*", record.description)
                tax = m.group(1) if m else ""
                evidence = int(m.group(2)) if m else 0
                prot = Protein(
                    uniprot_id=record.id.split("|")[1],
                    uniprot_db=record[1:2],
                    uniprot_gene=record.id.split("|")[2],
                    evidence_score=evidence,
                    tax_id=tax
                )
                prot.set_sequence(str(record.seq))
                prot.set_description(record.description)
                proteins.append(prot)
                count += 1
                if count >= cls.BATCH_SIZE:
                    batch += 1
                    Logger.info(f"Saving batch {batch} ...")
                    Protein.create_all(proteins)
                    proteins = []
                    count = 0
