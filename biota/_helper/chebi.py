import sys
import os
import csv
import re

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
    def parse_csv_from_file(path, file, delimiter='\t', quoting=csv.QUOTE_NONE) -> list:
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
        list__ = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter, quoting=quoting)
            for row in reader:
                list__.append( {key.lower() if type(key) == str else key: value for key, value in row.items()} )
        
        return list__

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

    @staticmethod
    def correction_of_chebi_file(path, file):
        """
        Correct the initial chebi obo file which contained syntax errors which prevented to use 
        the pronto package to parse the obo file

        This method read the initial obo file and create a corrected copy whose the name is given
        by the out_file parameter which is located in the same folder as the original file

        :type path: str
        :param path: Location of the file
        :type file: str
        :param file: Name of the original obo file
        :rtype: None
        """

        in_file = os.path.join(path, file)
        tab = in_file.split("/")
        n = len(tab)
        path = ("/").join(tab[0:n-1])
        in_filename = tab[-1]
        out_filename = 'corrected_'+in_filename
        out_file = os.path.join(path, './', out_filename)

        with open(in_file,'rt') as file: 
            with open(out_file,'wt') as outfile:
                for line in file.readlines():
                    m = re.search('xref: [a-zA-Z]+:([^\{\}\"]+) .*', line)
                    if m:
                        text = m.group(1)
                        corrected_text = text.replace(" ", "_")
                        outfile.write(line.replace(text, corrected_text))
                    else:
                        outfile.write(line)
        
        return path, out_filename