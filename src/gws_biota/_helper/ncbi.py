



class Taxonomy:
    """
    This module allows to all the ncbi taxonomy terms but also additionnal informations such as:
    parent id of terms, division, citations, etc..
    """

    @classmethod
    def __get_division(cls, division_file):
        """
        Use the division.dmp file to get a dictionnary that resume ncbi divisions.

        :type path: str
        :param path: location of the division.dmp file
        :type file: str
        :param file: name of the file
        :returns: dictionnary of ncbi classes in the format: {code: {"division code": str, "division name": str }}
        :rtype: dict

        """

        division_codes = {}
        with open(division_file) as fh:
            for line in fh.readlines():
                line = line.replace("\t|\n", "")
                infos = line.split("\t|\t")
                division_codes[infos[0]] = {"division cde": infos[1], "division name": infos[2]}
        return (division_codes)

    @classmethod
    def get_all_taxonomy(cls, dict_ncbi_names, ncbi_nodes_file, ncbi_division_file):
        """
        Get all ncbi taxonomy terms

        :type path: str
        :param path: location of the file
        :type dict_ncbi_names: dict
        :param dict_ncbi_names: dictionnary of names associated to ncbi terms
        :type file: dict
        :param file: input files names, especially nodes.dmp and names.dmp
        :returns: dictionnary of ncbi taxonomy terms in the following format
            {tax_id: {"tax_id": int, "ancestor": int, "rank": str, "division": str}}
        :rtype: dict
        """

        division = cls.__get_division(ncbi_division_file)
        dict_taxons = {}

        with open(ncbi_nodes_file) as fh:
            for line in fh:
                dict_single_tax = {}
                line = line.replace("\t|\n", "")
                infos = line.split("\t|\t")
                dict_single_tax['tax_id'] = infos[0]

                if infos[0] in dict_ncbi_names.keys():
                    dict_single_tax['name'] = dict_ncbi_names[infos[0]]

                dict_single_tax['ancestor'] = infos[1]
                dict_single_tax['rank'] = infos[2]

                if (infos[4] == ''):
                    dict_single_tax['division'] = "unspecified"
                else:
                    dict_single_tax['division'] = division[infos[4]]["division name"]

                dict_taxons[infos[0]] = dict_single_tax

            return (dict_taxons)

    @classmethod
    def get_ncbi_names(cls, ncbi_names_file):
        """
        Get all dictionnary of taxonomy id terms names

        :type path: str
        :param path: location of the file
        :type file: dict
        :param file: input files names, especially nodes.dmp and names.dmp
        :returns: dictionnary of ncbi taxonomy id terms names in the followinf format {tax_id: name}
        :rtype: dict
        """

        with open(ncbi_names_file) as fh:
            dict_ncbi_names = {}
            for line in fh.readlines():
                line = line.replace("\t|\n", "")
                infos = line.split("\t|\t")
                if infos[3] == "scientific name":
                    dict_ncbi_names[infos[0]] = infos[1]
        return (dict_ncbi_names)
