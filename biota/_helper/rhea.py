import sys
import os
import re
import pronto 
from pronto import Ontology
import csv

############################################################################################
#
#                                        Rhea parser
#                                         
############################################################################################

class Rhea():
    """

    This module allows to get list of biological reactions from rhea files and informations about thoses 
    reactions, such as master id, equations, substrates, products, biocyc id, kegg id, etc...

    """

    @staticmethod
    def parse_csv_from_file(path, file) -> list:
        """
        Parses a .tsv file and returns a list of dictionaries

        This method allows the user to get all informations in the spreadsheet. It is assumed that the firt row 
        of the spreadsheet is the location of the columns

        This tool accepts tab (\t) separated value files (.csv) as well as excel
        (.xls, .xlsx) files

        :type path: str
        :param path: location of the spreadsheet
        :type file: str
        :param file: name of the spreadsheet
        :returns: list of dictionnaries reapresenting rows of the spreadsheet
        :rtype: list
        """

        file_path = os.path.join(path, file)
        list__ = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                list__.append( {key.lower() if type(key) == str else key: value for key, value in row.items()} )
        
        return list__

    @staticmethod
    def parse_reaction_from_file(path, file):
        """
        Parses a rhea-kegg.reaction file of biological reactions and returns a list of dictionaries

        This tool accepts only the formated reaction file on which reaction are 
        described this way:

        ENTRY       RHEA:10022
        DEFINITION  (S)-2-amino-6-oxohexanoate + H(+) + L-glutamate + NADPH => H2O + L-saccharopine + NADP(+)
        EQUATION    CHEBI:58321 + CHEBI:15378 + CHEBI:29985 + CHEBI:57783 => CHEBI:15377 + CHEBI:57951 + CHEBI:58349

        and reactions are separated by the "///" symbol

        :type path: str
        :param path: location of the file
        :type file: str
        :param file: name of the file
        :returns: list of dictionnaries reapresenting reactions
        :rtype: list
        """

        file_path = os.path.join(path, file)
        with open(file_path) as fh:
            contents = fh.read()
            list_content = contents.split('///')
            list_reaction = []
            for cont in list_content:
                m1 = re.search("ENTRY\s+(.*)", cont)
                m2 = re.search("DEFINITION\s+(.*)", cont)
                m3 = re.search("EQUATION\s+(.*)", cont)
                m4 = re.search("ENZYME\s+(.*)", cont, flags=re.DOTALL)
                dict__ = {}
                if m1:
                    dict__["entry"] = m1[1]
                
                if m2:
                    dict__["definition"] = m2[1]
                    
                if m3:
                    dict__["equation"] = m3[1]
                    
                if m4:
                    dict__["enzymes"] = m4[1].split()
                
                if 'equation' in dict__.keys():
                    dict__['source_equation'] = dict__['equation']   
                    if len(re.findall(' =>', dict__['equation'])) > 0:
                        list_compound  = dict__['equation'].split(" => ")

                    elif len(re.findall('<=>', dict__['equation'])) > 0:
                        list_compound  = dict__['equation'].split(" <=> ")

                    elif len(re.findall(' = ', dict__['equation'])) > 0:
                        list_compound  = dict__['equation'].split(" = ")
                
                reagents = list_compound[0]
                products = list_compound[1]
                delimiters = ","," + "
                regexPattern = '|'.join(map(re.escape, delimiters))
                list_substrates = re.split(regexPattern, reagents)
                list_products = re.split(regexPattern, products)
                list_dict_s = []
                list_dict_p = []

                for i in range(0, len(list_substrates)):
                    list_substrates[i] = re.sub(' $', '', list_substrates[i])
                
                for i in range(0, len(list_products)):
                    list_products[i] = re.sub(' $', '', list_products[i])

                dict__['equation'] = {}
                
                dict_substrates = {}
                for i in range(0, len(list_substrates)):
                    if ' ' in list_substrates[i]:
                        coeff_compound = re.split(' ', list_substrates[i])
                        compound = coeff_compound[1]
                        coeff = coeff_compound[0]
                        dict_substrates[compound] = coeff
                        list_dict_s.append(compound)
                    else:
                        dict_substrates[list_substrates[i]] = 1
                        list_dict_s.append(list_substrates[i])

                dict__['substrates'] = list_dict_s
                dict__['equation']["substrates"] = dict_substrates
                
                dict_products = {}
                for i in range(0, len(list_products)):
                    if ' ' in list_products[i]:
                        coeff_compound = re.split(' ', list_products[i])
                        compound = coeff_compound[1]
                        coeff = coeff_compound[0]
                        dict_products[compound] = int(coeff)
                        list_dict_p.append(compound)
                    else:
                        dict_products[list_products[i]] = 1
                        list_dict_p.append(list_products[i])
                
                dict__['products'] = list_dict_p
                dict__['equation']['products'] = dict_products
            
                if dict__:           
                    list_reaction.append(dict__)
        
        return list_reaction

    
    @staticmethod
    def get_columns_from_lines(list_lines):
        """
        Parses a list of dictionnaries get from using the parse_csv_from_file() method on
        rhea-directions.tsv file.

        Each dictionnaries of the input list are formated this way:
        {'rhea_id_master': rhea_id, 'rhea_id_lr': rhea_id, 'rhea_id_rl': rhea_id, 'rhea_id_bi': rhea_id} 
        
        Returns differents lists correponding to sets of reactions 
        directed in a specific direction.

        This method allows to separate reactions id by specific directions. rhea_master is the list
        of master reaction id

        :type list_lines:
        :param list_lines:
        :returns: rhea_master, rhea_id_LR, rhea_id_RL, rhea_id_BI, lists of reactions id in a specific direction
        :rtype: list 
        
        """

        cols = {
            "UN": [],
            "LR": [],
            "RL": [],
            "BI": []
        }

        for dict in list_lines:
            cols["UN"].append(dict['rhea_id_master'])
            cols["LR"].append(dict['rhea_id_lr'])
            cols["RL"].append(dict['rhea_id_rl'])
            cols["BI"].append(dict['rhea_id_bi'])

        return cols
