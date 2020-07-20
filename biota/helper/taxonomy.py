import sys
import os
import re

############################################################################################
#
#                                        Taxonomy parser
#                                         
############################################################################################

class Taxo():
    @classmethod
    def __get_division(cls, path, file):
        file_path = os.path.join(path, file)
        division_codes = {}
        with open(file_path) as fh:
            for line in fh.readlines():
                line = line.replace("\t|\n", "")
                infos = line.split("\t|\t")
                division_codes[infos[0]] = {"division cde": infos[1], "division name": infos[2] }
        return(division_codes)
    
    @classmethod
    def get_ncbi_names(cls, path, **files):
        names_path = os.path.join(path, files['ncbi_names'])
        with open(names_path) as fh:
            dict_ncbi_names = {}
            for line in fh.readlines():
                line = line.replace("\t|\n", "")
                infos = line.split("\t|\t")
                if infos[3] == "scientific name":
                    dict_ncbi_names[infos[0]] = infos[1]
        return(dict_ncbi_names)

    @classmethod
    def get_all_taxonomy(cls, path, dict_ncbi_names, **files):
        nodes_path = os.path.join(path, files['ncbi_nodes'])
        division = cls.__get_division(path, files["ncbi_division"])
        dict_taxons = {}
        
        with open(nodes_path) as fh:

            for line in fh:
                dict_single_tax = {}
                line = line.replace("\t|\n", "")
                infos = line.split("\t|\t")
                dict_single_tax['tax_id'] = infos[0]

                if infos[0] in dict_ncbi_names.keys():
                    dict_single_tax['name'] = dict_ncbi_names[infos[0]]

                dict_single_tax['ancestor'] = infos[1]
                dict_single_tax['rank'] = infos[2]

                if(infos[4] == ''):
                    dict_single_tax['division'] = "unspecified"
                else:
                    dict_single_tax['division'] = division[infos[4]]["division name"]

                dict_taxons[infos[0]] = dict_single_tax

            return(dict_taxons)
