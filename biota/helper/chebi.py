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

    @staticmethod
    def parse_csv_from_file(path, file) -> list:
        """
        Parses a chebi tsv file of chemicals and returns a list of dictionaries
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
            #status = 'test ok'
        return(list__)

    @staticmethod
    def parse_csv_from_list(path, file, infos = list) -> list:
        
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
            #status = 'test ok'
        return(list__)

    @staticmethod
    def create_ontology_from_file(path, file):
        file_path = os.path.join(path, file)
        onto = Ontology(file_path)
        return onto
        
    @staticmethod
    def parse_onto_from_ontology(ontology):
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