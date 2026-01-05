

from brendapy import BrendaParser, BrendaSettings


class Brenda:
    """
    This module allows to get list of dictionnaries where terms represents brenda proteins/enzymes
    """
    parser = None  # reuse parser

    def __init__(self, brenda_file, taxonomy_dir=None, bto_file=None, chebi_file=None):
        BrendaSettings.initialize_data_dir(
            brenda_file=brenda_file, taxonomy_dir=taxonomy_dir, bto_file=bto_file, chebi_file=chebi_file)
        self.parser = BrendaParser(brenda_file=brenda_file)

    def parse_all_enzyme_to_dict(self):
        """
        Uses the package brandapy to parses the brenda_download.txt file and returns a list of dictionnaries
        where terms represent proteins filled with their informations (experimental properties, citations, synonyms, etc...).

        :returns: list of all brenda proteins
        :rtype: list
        """
        list_proteins = []
        list_deprecated_ec = []
        for ec in self.parser.keys():
            proteins, deprecated_ec = self.parser.get_all_proteins(ec)

            if deprecated_ec:
                list_deprecated_ec.append(deprecated_ec)

            for p in proteins.values():
                for k in p.data:
                    if isinstance(p.data[k], set):
                        p.data[k] = list(p.data[k])
                        p.data[k].sort()

                    # only keep pubmed ids if possible
                    if k == 'references':
                        for idx in p.data[k]:
                            if "pubmed" in p.data[k][idx]:
                                p.data[k][idx] = p.data[k][idx]["pubmed"]
                            else:
                                p.data[k][idx] = p.data[k][idx]["info"]

                list_proteins.append(p.data)

        return list_proteins, list_deprecated_ec
