import sys
import os
import unittest

import pronto 
from pronto import Ontology

############################################################################################
#
#                                        Chebi class
#                                         
############################################################################################

class Chebi():
    """

    This module allows to get list of dictionnaries where terms represents chebi chemical compounds and 
    to get list of dictionnaries where terms represents chebi ontology terms

    """

    @staticmethod
    def parse_csv_from_file(path, file) -> list:
        """
        Parses a chebi .tsv file of chemicals entities and returns a list of dictionaries

        This method allows the user to get all informations in the spreadsheet. It is assumed that the firt row 
        of the spreadsheet is the location of the columns

        This tool accepts tab (\t) separated value files (.csv) as well as excel
        (.xls, .xlsx) files

        :type path: str
        :param path: Location of the spreadsheet
        :type file: str
        :param file: Name of the spreadsheet
        :returns: list of dictionnaries reapresenting rows of the spreadsheet
        :rtype: list
        """

        file_path = os.path.join(path, file)
        with open(file_path) as fh:
            line_count = 0
            list__ = []
            for line in fh.readlines():
                if(line_count < 1):
                    if('\t' not in line):
                        raise Exception("csv-parser", "invalid type of file", "separation character must be a TAB")
                    else:
                        infos_table = line.split('\t')
                        line_count +=1
                else:
                    list_row = []
                    list_row = line.split('\t')
                    dict_compound = {}

                    if(len(list_row) == len(infos_table)):
                        for i in range(0, len(infos_table)):
                                dict_compound[infos_table[i].lower().replace('\n', '')] = list_row[i].replace('\n', '')
                    else:
                        for i in range(0, len(list_row)):
                            dict_compound[infos_table[i].lower().replace('\n', '')] = list_row[i].replace('\n', '') 
                    
                    list__.append(dict_compound)
                    line_count += 1
        return(list__)

    @staticmethod
    def parse_csv_from_list(path, file, infos = list) -> list:
        """
        Parses a chebi tsv file of chemicals entities and returns a list of dictionaries

        This method allows the user to get all informations in the spreadsheet. It is assumed that the paramater
        infos indicates location of the columns

        This tool accepts tab (\t) separated value files (.csv) as well as excel
        (.xls, .xlsx) files

        :type path: str
        :param path: Location of the spreadsheet
        :type file: str
        :param file: Name of the obo file
        :type infos: list
        :param infos: list of names of columns of the spreadsheet
        :returns: list of dictionnaries reapresenting rows of the spreadsheet
        :rtype: list
        """

        file_path = os.path.join(path, file)
        with open(file_path) as fh:
            if isinstance(infos, list):
                line_count = 0
                list__ = []
                infos_table = infos
                for line in fh.readlines():
                    if(line_count < 1):
                        infos_table = line.split('\t')
                        line_count +=1
                    else:
                        list_row = []
                        list_row = line.split('\t')
                        dict_compound = {}

                        if(len(list_row) == len(infos_table)):
                            for i in range(0, len(infos_table)):
                                    dict_compound[infos_table[i].lower().replace('\n', '')] = list_row[i].replace('\n', '')
                        else:
                            for i in range(0, len(list_row)):
                                dict_compound[infos_table[i].lower().replace('\n', '')] = list_row[i].replace('\n', '') 
                        
                        list__.append(dict_compound)
                        line_count += 1
            else:
                raise Exception("Chebi", "parse_csv_from_list",  "invalid type")
        return(list__)

    @staticmethod
    def create_ontology_from_file(path, file):
        """
        Create the chebi ontology from the markup language file chebi.obo

        This method allows the create an ontalogy from an .obo file.

        :type path: str
        :param path: Location of the spreadsheet
        :type file: str
        :param file: Name of the spreadsheet
        :returns: Ontology object from the package pronto
        :rtype: Ontology
        """

        file_path = os.path.join(path, file)
        onto = Ontology(file_path)
        return onto
        
    @staticmethod
    def parse_onto_from_ontology(ontology):
        """
        Parses a chebi ontology and returns a list of dictionnaries where each elements represent an ontology terms

        This method allows the user to format all the chebi ontology in readable and usable terms.

        This tool accepts only Ontology object created from the package pronto

        :type ontology: Ontology
        :param path: chebi ontology
        :returns: list of dictionnaries reapresenting all terms of the ontology
        :rtype: list
        """

        list_chebi_term = []
        for term in ontology.terms():
            dict_term = {}
            dict_term['id'] = term.id
            dict_term['name'] = term.name.replace('\r', '')
            dict_term['definition'] = term.definition
            dict_term['alt_id'] = list(term.alternate_ids)
            #dict_term['synonyms'] = list(term.synonyms)
            #dict_term['subsets'] = term.subsets
            #dict_term['property_value'] = list(term.annotations)
            #dict_term['xrefs'] = list(term.xrefs)
            list_chebi_term.append(dict_term)
        
        return(list_chebi_term)