# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Folder, Logger
from Bio import Entrez
import xml.dom.minidom
import os


class Pubmed():
    @classmethod
    def get_all_pubmed_articles(cls, destination_dir, uids):
        Logger.info(f"Number of elements : {len(uids['IdList'])}")

        for pmid in uids['IdList']:
            try:
                # Retrieve item details in XML format
                handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
                article = handle.read()
                Logger.info(f"article : {article}")
                handle.close()

                file_path = os.path.join(destination_dir, f"pmid_{pmid}.txt")

                with open(file_path, "w") as file:
                    file.write(article)

                # # Load XML
                # dom = xml.dom.minidom.parseString(article_xml)

                # # Add newlines and indentation
                # pretty_xml = dom.toprettyxml(indent="  ")

                # # Generate file path
                # file_path = os.path.join(destination_dir, f"article_{pmid}.xml")

                # # Save the reformatted XML to a file
                # with open(file_path, "w", encoding="utf-8") as file:
                #     file.write(pretty_xml)

            except Exception as inst:
                print(f"An error has occurred : {inst}")

        return Folder(destination_dir)
