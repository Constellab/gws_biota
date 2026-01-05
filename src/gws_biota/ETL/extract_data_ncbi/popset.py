# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os

from Bio import Entrez
from gws_core import Folder, Logger


class PopSet:
    @classmethod
    def get_popset_data(cls, destination_dir, uids) -> Folder:
        Logger.info(f"Number of elements : {len(uids['IdList'])}")

        # Download data with Entrez (NCBI database API)
        for uid in uids["IdList"]:
            handle = Entrez.efetch(db="popset", id=uid, rettype="fasta", retmode="text")
            xml_data = handle.read()
            Logger.info(f"xml data : {xml_data}")
            handle.close()

            file_path = os.path.join(destination_dir, f"popset_{uid}.txt")

            with open(file_path, "w") as file:
                file.write(xml_data)

        return Folder(destination_dir)
