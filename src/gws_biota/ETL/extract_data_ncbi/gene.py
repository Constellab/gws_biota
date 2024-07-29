# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Folder, Logger

from Bio import Entrez
import os


class Gene():
    @classmethod
    def get_gene_data(cls, destination_dir, uids) -> Folder:
        uids = uids['IdList']

        # Download data with Entrez (NCBI database API)
        for uid in uids:
            try:
                gene_handle = Entrez.efetch(db="gene", id=uid, rettype="gene_table", retmode="text")
                gene_record = gene_handle.read()
                gene_handle.close()

                file_path = os.path.join(destination_dir, f"gene_{uid}.txt")

                try:
                    with open(file_path, "w") as output_file:
                        output_file.write(gene_record)
                except IOError as e:
                    Logger.info(f"Failed to write file {file_path}: {e}")
                    Logger.error(f"Failed to write file {file_path}: {e}")

            except Exception as e:
                Logger.info(f"Failed to fetch gene data for UID {uid}: {e}")
                Logger.error(f"Failed to fetch gene data for UID {uid}: {e}")

        return Folder(destination_dir)
