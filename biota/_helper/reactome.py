import sys
import os
import re
import csv

class Reactome():
    
    @staticmethod
    def parse_to_dict(path, file, delimiter="\t", quoting=csv.QUOTE_NONE, fieldnames=[]) -> list:
        """
        Parses a .csv file

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
            reader = csv.DictReader(csvfile, delimiter=delimiter, quoting=quoting, fieldnames=fieldnames)
            for row in reader:
                list__.append( {key.lower() if type(key) == str else key: value for key, value in row.items()} )
        
        return list__
    
    @staticmethod
    def parse_pathways_to_dict(path, file) -> list:

        fieldnames = ["reactome_pathway_id", "title", "species"]
        return Reactome.parse_to_dict(path, file, fieldnames=fieldnames)
        
    
    @staticmethod
    def parse_pathway_relations_to_dict(path, file) -> list:
        
        fieldnames = ["ancestor", "reactome_pathway_id"]
        return Reactome.parse_to_dict(path, file, fieldnames=fieldnames)
    
    @staticmethod
    def parse_chebi_pathway_to_dict(path, file) -> list:
 
        fieldnames = ["chebi_id", "reactome_pathway_id", "url", "pathway_name", "code", "species"]
        return Reactome.parse_to_dict(path, file, fieldnames=fieldnames)