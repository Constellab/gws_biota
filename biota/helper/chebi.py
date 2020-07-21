import sys
import os
import pronto 
from pronto import Ontology
import csv

############################################################################################
#
#                                        Chebi class
#                                         
############################################################################################

class Chebi():

    @staticmethod
    def parse_csv_from_file(path, file) -> list:
        file_path = os.path.join(path, file)
        list__ = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                list__.append( {key.lower() if type(key) == str else key: value for key, value in row.items()} )
        
        return list__

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