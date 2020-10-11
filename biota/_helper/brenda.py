
import sys
import re
import os
from brendapy import BrendaParser

############################################################################################
#
#                                        Brenda class
#                                         
############################################################################################

class Brenda():
    """
    This module allows to get list of dictionnaries where terms represents brenda proteins/enzymes
    """
    parser = None  # reuse parser

    def __init__(self, file_path):
        self.parser = BrendaParser(brenda_file = file_path)
    
    def parse_all_enzyme_to_dict(self):
        """
        Uses the package brandapy to parses the brenda_download.txt file and returns a list of dictionnaries
        where terms represent proteins filled with their informations (experimental properties, citations, synonyms, etc...). 

        :returns: list of all brenda proteins
        :rtype: list
        """
        list_proteins = []
        for ec in self.parser.keys():
            proteins = self.parser.get_proteins(ec)
            for p in proteins.values():
                for k in p.data:
                    if isinstance(p.data[k], set):
                        p.data[k] = list(p.data[k])
                        p.data[k].sort()

                    # only keep pubmed ids if possible
                    if k == 'references':
                        for idx in p.data[k]:
                            if "pubmed" in p.data[k][idx]:
                                p.data[k][idx] =  p.data[k][idx]["pubmed"]
                            else:
                                p.data[k][idx] =  p.data[k][idx]["info"]

                list_proteins.append(p.data)

        return(list_proteins)
