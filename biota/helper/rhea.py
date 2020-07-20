import sys
import os
import re
import pronto 
from pronto import Ontology

############################################################################################
#
#                                        Rhea parser
#                                         
############################################################################################

class Rhea():

    @staticmethod
    def parse_csv_from_file(path, file) -> list:
        file_path = os.path.join(path, file)
        with open(file_path) as fh:
            line_count = 0
            list__ = []
            for line in fh.readlines():
                if line_count < 1:
                    if('\t' not in line):
                        raise Exception("csv-parser", "invalid type of file", "separation character must be a TAB")
                    else:
                        infos_table = line.split('\t')
                        line_count +=1
                else:
                    list_row = []
                    list_row = line.split('\t')
                    dict_compound = {}

                    if len(list_row) == len(infos_table):
                        for i in range(0, len(infos_table)):
                            dict_compound[infos_table[i].lower().replace('\n', '')] = list_row[i].replace('\n', '')
                    else:
                        for i in range(0, len(list_row)):
                            dict_compound[infos_table[i].lower().replace('\n', '')] = list_row[i].replace('\n', '') 
                    
                    list__.append(dict_compound)
                    line_count += 1

        return(list__)

    @staticmethod
    def parse_reaction_from_file(path, file):
        file_path = os.path.join(path, file)
        with open(file_path) as fh:
            contents = fh.read()
            list_content = contents.split('///')
            list_reaction = []
            for cont in list_content:
                dict__ = {}
                infos_reaction = cont.split('\n)\n')
                part_one = infos_reaction[0]
                for infos in part_one.split('\n'):
                    m = re.findall(' {2,12}', infos)
                    if (len(m) > 0):
                        list_infos = infos.split(m[0])
                        if (list_infos[0] not in dict__.keys() and list_infos[0] != 'ENZYME'):
                            dict__[list_infos[0].lower()] = list_infos[1]
                        elif (list_infos[0] == 'ENZYME'):
                            list_enzyme = []
                            for j in range(1, len(list_infos)):
                                n = re.findall(' {1,4}', list_infos[j])
                                if(len(n) > 0):
                                    list_enzyme.append(list_infos[j].replace(n[0], ''))
                                else:
                                    list_enzyme.append(list_infos[j])
                            dict__['enzyme'] = list_enzyme
                            
                if('equation' in dict__.keys()):
                    dict__['source_equation'] = dict__['equation']   
                    if (len(re.findall(' =>', dict__['equation'])) > 0):
                        list_compound  = dict__['equation'].split(" => ")

                    elif(len(re.findall('<=>', dict__['equation'])) > 0):
                        list_compound  = dict__['equation'].split(" <=> ")

                    elif(len(re.findall(' = ', dict__['equation'])) > 0):
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
                    if (' ' in list_substrates[i]):
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
                    if (' ' in list_products[i]):
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
            
                if(len(infos_reaction) >= 2):
                    part_two = infos_reaction[1]
                    m = re.findall(' {2,12}', part_two)
                    if (len(m) > 0):
                        list_infos = part_two.split(m[0])
                        if (list_infos[0] not in dict__.keys()):
                            dict__[list_infos[0]] = list_infos[1]
                if(dict__ != {}):           
                    list_reaction.append(dict__)
        return(list_reaction)

    @staticmethod
    def parse_compound_from_file(path, file):
        file_path = os.path.join(path, file)
        with open(file_path) as fh:
            contents = fh.read()
            list_content = contents.split('///')
            list_dict = []
            for cont in list_content:
                dict__ = {}
                for infos in cont.split('\n'):
                    m = re.findall(' {2,12}', infos)
                    if (len(m) > 0):
                        list_infos = infos.split(m[0])
                        if (list_infos[0] not in dict__.keys() and list_infos[0] != '' and list_infos[0] != "ENZYME"):
                            dict__[list_infos[0].lower()] = list_infos[1]
                        elif (list_infos[0] == ''):
                            if('enzyme' not in dict__.keys()):
                                dict__['reaction'] += " "+ list_infos[1]
                        elif (list_infos[0] == 'ENZYME'):
                            list_enzyme = []
                            for j in range(1, len(list_infos)):
                                list_enzyme.append(list_infos[j])
                            dict__['enzyme'] = list_enzyme
                        #### convert dict__['REACTION'] in a list ###
                if('reaction' in dict__.keys()):
                    str_reaction = dict__['reaction']
                    dict__['reaction'] = str_reaction.split(' ')
                    list_dict.append(dict__)
        return(list_dict)

    @staticmethod
    def create_ontology_from_owl(path, file):
        file_path = os.path.join(path, file)
        onto = Ontology(file_path)
        return onto
    
    @staticmethod
    def get_columns_from_lines(list_lines):
        rhea_master = []
        rhea_id_LR = []
        rhea_id_RL = []
        rhea_id_BI = []
        for dict in list_lines:
            rhea_master.append(dict['rhea_id_master'])
            rhea_id_LR.append(dict['rhea_id_lr'])
            rhea_id_RL.append(dict['rhea_id_rl'])
            rhea_id_BI.append(dict['rhea_id_bi'])
        return(rhea_master, rhea_id_LR, rhea_id_RL, rhea_id_BI)




    # @staticmethod
    # def from_owl_to_obo(path, file, filename_):
    #     file_path = os.path.join(path, file)
    #     save_path = os.path.realpath('./databases_input')
    #     complete_name = os.path.join(save_path, filename_+".obo")
    #     edam = Ontology(file_path)
    #     with open(complete_name, "wb") as f:
    #         edam.dump(f, format='obo')