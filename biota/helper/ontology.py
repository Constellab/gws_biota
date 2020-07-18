import sys
import os
import pronto 
from pronto import Ontology
import json
import re

############################################################################################
#
#                                       Ontology class
#                                         
############################################################################################

class Onto():
    
    #---------- create and correction functions --------------#
    @staticmethod
    def correction_of_sbo_file(path, file, out_file):
        with open(os.path.join(path, file),'rt') as file: 
            with open(os.path.join(path, out_file ),'wt') as outfile:
                for line in file.readlines():
                    if line.startswith('synonym'):
                        if ' []' in line:
                            outfile.write(line.replace(' []', ' EXACT []'))
                    else:
                        outfile.write(line)

    @staticmethod
    def create_ontology_from_obo(path, file):
        file_path = os.path.join(path, file)
        onto = Ontology(file_path)
        return onto

    @staticmethod
    def create_ontology_from_owl(path, file):
        file_path = os.path.join(path, file)
        onto = Ontology(file_path)
        return onto

    #---------- parsing functions --------------#
    @staticmethod
    def parse_bto_from_json(path,file):
        list_bto = []
        with open(os.path.join(path, file)) as json_bto_data:
            data = json.load(json_bto_data)
            for key in data.keys():
                dict_bto = {}
                if data[key] == {}:
                    pass
                else:
                    dict_bto['id'] = data[key]['key']
                    dict_bto['label'] = data[key]['label']
                    if('ancestors' in data[key].keys()):
                        dict_bto['ancestors'] = data[key]['ancestors']
                    if ('synonyms' in data[key].keys() ):
                        dict_bto['synonyms'] = data[key]['synonyms']
                list_bto.append(dict_bto)

        return(list_bto)
    
    @staticmethod
    def parse_eco_terms_from_ontoloy(ontology):
        list_eco = []
        for term in ontology.terms():
            dict_eco = {}
            dict_eco['id'] = term.id
            dict_eco['name'] = term.name.replace('\r', '')
            dict_eco['definition'] = str(term.definition) #str 
            #dict_eco['synonyms'] = list(term.synonyms)
            # ------ get ancestors ------ #
            try:
                sup = term.superclasses(distance = 1, with_self = False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_eco['ancestors'] = []
                    for data in fro:
                        dict_eco['ancestors'].append(data)
            except:
                pass
                #print('ancestors not in the ontology')

            list_eco.append(dict_eco)
        return(list_eco)

    @staticmethod
    def parse_obo_from_ontology(ontology):
        list_go = []
        for term in ontology.terms():
            dict_go = {}
            dict_go['id'] = term.id
            dict_go['name'] = term.name.replace('\r', '')
            dict_go['namespace'] = term.namespace.replace('\r', '')
            dict_go['definition'] = str(term.definition) #str
            #dict_go['xrefs'] = term.xrefs 
            # ------ get xrefs ------#
            try:
                xrefs_fro = term.xrefs
                if len(xrefs_fro) > 0 :
                    dict_go['xrefs'] = []
                    for data in xrefs_fro:
                        dict_go['xrefs'].append(data.id)
            except:
                pass
                #print('can not extract xrefs')

            # ------ get ancestors ------ #
            try:
                sup = term.superclasses(distance = 1, with_self = False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_go['ancestors'] = []
                    for data in fro:
                        dict_go['ancestors'].append(data)
            except:
                pass
                #print('ancestors not in the ontology')

            if 'xrefs' in dict_go:
                for data in dict_go['xrefs']:
                    list_rhea_id = []
                    if 'RHEA' in data:
                        list_rhea_id.append(data)
                    if len(list_rhea_id) > 0:
                        dict_go['rhea_id'] = []
                        dict_go['rhea_id'] = list_rhea_id
            #dict_go['synonyms'] = list(term.synonyms)

            list_alt_ids = list(term.alternate_ids)
            if len(list_alt_ids) > 0:
                dict_go['alt_id'] = list_alt_ids

            list_go.append(dict_go)

        return(list_go)

    @staticmethod
    def parse_sbo_terms_from_ontology(ontology):
        list_sbo = []
        for term in ontology.terms():
            dict_sbo = {}
            dict_sbo['id'] = term.id
            dict_sbo['name'] = term.name.replace('\r', '')

            if '</math>' in term.definition:
                list_def = term.definition.split("<math xmlns")
                def_ = list_def[0]
                dict_sbo['definition'] = def_.capitalize()
            else:
                dict_sbo['definition'] = term.definition.capitalize()

            try:
                sup = term.superclasses(distance = 1, with_self = False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_sbo['ancestors'] = []
                    for data in fro:
                        dict_sbo['ancestors'].append(data)
            except:
                pass
                #print('ancestors not in the ontology')

            list_sbo.append(dict_sbo)

        return(list_sbo)
    
    #---------- owl to obo converter --------------#
    @staticmethod
    def from_owl_to_obo(path, file, filename_):
        file_path = os.path.join(path, file)
        save_path = os.path.realpath('./databases_input')
        complete_name = os.path.join(save_path, filename_+".obo")
        edam = Ontology(file_path)
        with open(complete_name, "wb") as f:
            edam.dump(f, format='obo')