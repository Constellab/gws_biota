

import os
import re

from gws_core import Logger


class Chebi:
    """
    This module allows to get list of dictionnaries where terms represents chebi chemical compounds and
    to get list of dictionnaries where terms represents chebi ontology terms
    """

    @staticmethod
    def correction_of_chebi_file(path, compound_file: str):
        """
        Correct the initial chebi obo file which contained syntax errors which prevented to use
        the pronto package to parse the obo file

        This method read the initial obo file and create a corrected copy whose the name is given
        by the out_file parameter which is located in the same folder as the original file

        :type file: str
        :param file: path of the original obo file
        :rtype: None
        """
        in_file = os.path.join(path, compound_file)
        Logger.info(f"in file : {in_file}")

        tab = in_file.split("/")
        n = len(tab)
        path = ("/").join(tab[0:n-1])
        in_filename = tab[-1]

        out_filename = 'corrected_'+in_filename
        out_file = os.path.join(path, out_filename)
        Logger.info(f"out_file : {out_file}")

        with open(in_file, encoding='utf-8') as file:
            with open(out_file, "w", encoding='utf-8') as outfile:
                for line in file.readlines():
                    m = re.search(r'xref: [a-zA-Z]+:([^\{\}\"]+) .*', line)
                    if m:
                        text = m.group(1)
                        corrected_text = text.replace(" ", "_")
                        outfile.write(line.replace(text, corrected_text))
                    else:
                        outfile.write(line)

        return path, out_filename
