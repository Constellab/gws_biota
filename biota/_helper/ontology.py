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
    """
    
    This module allows to get all ontologie that will be used by the Gencovery web application.
    
    This include GO, SBO, BTO and ECO ontologies

    """
    
    @staticmethod
    def correction_of_sbo_file(path, file):
        """
        Correct the initial sbo.obo file which contained syntax errors which prevented to use 
        the pronto package to parse the obo file

        This method read the initial obo file and create a corrected copy whose the name is given
        by the out_file parameter which is located in the same folder as the original file

        :type path: str
        :param path: Location of the file
        :type file: str
        :param out_file: Name of the corrected obo file
        :rtype: None
        """

        in_file = os.path.join(path, file)
        
        tab = in_file.split("/")
        n = len(tab)
        path = ("/").join(tab[0:n-1])
        in_filename = tab[-1]

        out_filename = 'corrected_'+in_filename
        out_file = os.path.join(path, out_filename)

        with open(in_file,'rt') as file: 
            with open(out_file,'wt') as outfile:
                for line in file.readlines():
                    if line.startswith('synonym'):
                        if ' []' in line:
                            outfile.write(line.replace(' []', ' EXACT []'))
                    else:
                        outfile.write(line)

        return path, out_filename

    @staticmethod
    def correction_of_pwo_file(path, file):
        """
        Correct the initial pwo obo file which contained syntax errors which prevented to use 
        the pronto package to parse the obo file

        This method read the initial obo file and create a corrected copy whose the name is given
        by the out_file parameter which is located in the same folder as the original file

        :type path: str
        :param path: Location of the file
        :type file: str
        :param out_file: Name of the corrected obo file
        :rtype: None
        """

        in_file = os.path.join(path, file)
        
        tab = in_file.split("/")
        n = len(tab)
        path = ("/").join(tab[0:n-1])
        in_filename = tab[-1]

        out_filename = 'corrected_'+in_filename
        out_file = os.path.join(path, out_filename)

        with open(in_file,'rt') as file: 
            with open(out_file,'wt') as outfile:
                for line in file.readlines():
                    m = re.search('\[(.+)\]', line)
                    if m:
                        text = m.group(1)
                        entries = text.replace("\,","##").split(",")
                        for i in range(0, len(entries)):
                            entries[i] = entries[i].strip().replace(" ", "-")     
                        
                        corrected_text = ", ".join(entries)  
                        outfile.write(line.replace(text, corrected_text).replace("##", "\,"))
                    else:
                        outfile.write(line)

        return path, out_filename

    @staticmethod
    def create_ontology_from_obo(path, file):
        """
        This method allows the create an ontalogy from an .owl file.

        :type path: str
        :param path: Location of the file
        :type file: str
        :param file: Name of the obo file
        :returns: Ontology object from the package pronto
        :rtype: Ontology
        """
        file_path = os.path.join(path, file)
        onto = Ontology(file_path)
        return onto

    @staticmethod
    def parse_bto_from_json(path,file):
        """
        Create the bto ontology from a json file

        :type path: str
        :param path: Location of the file
        :type file: str
        :param file: Name of the json file
        :returns: Ontology object from the package pronto
        :rtype: Ontology
        """
        list_bto = []
        with open(os.path.join(path, file)) as json_bto_data:
            data = json.load(json_bto_data)
            for key in data.keys():
                dict_bto = {}
                if data[key] == {}:
                    pass
                else:
                    dict_bto['id'] = data[key]['key']
                    dict_bto['title'] = data[key]['label']
                    if('ancestors' in data[key].keys()):
                        dict_bto['ancestors'] = data[key]['ancestors']
                    if ('synonyms' in data[key].keys() ):
                        dict_bto['synonyms'] = data[key]['synonyms']
                list_bto.append(dict_bto)

        return(list_bto)
    
    @staticmethod
    def parse_eco_terms_from_ontoloy(ontology):
        """
        Create eco ontology terms from a Ontology object

        :type ontology: Ontology
        :param ontology: ECO ontology created by the create_ontology_from_obo method
        :returns: list on dictionnaries where each terms represents an eco ontology term
        :rtype: list
        """
        list_eco = []
        for term in ontology.terms():
            dict_eco = {}
            dict_eco['id'] = term.id
            dict_eco['title'] = term.name.replace('\r', '')
            dict_eco['definition'] = str(term.definition) #str 

            try:
                sup = term.superclasses(distance = 1, with_self = False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_eco['ancestors'] = []
                    for data in fro:
                        dict_eco['ancestors'].append(data)
            except:
                pass

            list_eco.append(dict_eco)
        return(list_eco)

    @staticmethod
    def parse_obo_from_ontology(ontology):
        """
        Create an ontology from a Ontology object

        :type ontology: Ontology
        :param ontology: ontology created by the create_ontology_from_obo method
        :returns: list on dictionnaries where each terms represents an ontology term
        :rtype: list
        """
        list_go = []
        for term in ontology.terms():
            dict_go = {}
            dict_go['id'] = term.id
            dict_go['title'] = term.name.replace('\r', '')
            dict_go['namespace'] = term.namespace.replace('\r', '')
            dict_go['definition'] = str(term.definition) #str

            # ------ get xrefs ------#
            try:
                xrefs_fro = term.xrefs
                if len(xrefs_fro) > 0 :
                    dict_go['xrefs'] = []
                    for data in xrefs_fro:
                        dict_go['xrefs'].append(data.id)
            except:
                pass

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
        """
        Create sbo ontology terms from a Ontology object

        :type ontology: Ontology
        :param ontology: SBO ontology created by the create_ontology_from_obo method
        :returns: list on dictionnaries where each terms represents a sbo ontology term
        :rtype: list
        """
        list_sbo = []
        for term in ontology.terms():
            dict_sbo = {}
            dict_sbo['id'] = term.id
            dict_sbo['title'] = term.name.replace('\r', '')

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

            list_sbo.append(dict_sbo)

        return(list_sbo)
    
    @staticmethod
    def from_owl_to_obo(path, file, filename_):
        """
        Use the pronto package to convert a .owl to a .obo file

        :type path: str
        :param path: Location of the file
        :type file: str
        :param file: Name of the original owl file
        :type filename_: str
        :param filename_: Name of the converted obo file

        :rtype: None
        """
        file_path = os.path.join(path, file)
        save_path = os.path.realpath('./databases_input')
        complete_name = os.path.join(save_path, filename_+".obo")
        edam = Ontology(file_path)
        with open(complete_name, "wb") as f:
            edam.dump(f, format='obo')


    @staticmethod
    def parse_pwo_terms_from_ontology(ontology):
        """
        Create pathway ontology terms from a Ontology object

        :type ontology: Ontology
        :param ontology: Pathway ontology created by the create_ontology_from_obo method
        :returns: list on dictionnaries where each terms represents an pwo ontology term
        :rtype: list
        """
        list_pwo = []
        for term in ontology.terms():
            dict_pwo = {}
            dict_pwo['id'] = term.id
            dict_pwo['title'] = term.name.replace('\r', '')
            dict_pwo['definition'] = str(term.definition) #str 

            try:
                sup = term.superclasses(distance = 1, with_self = False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_pwo['ancestors'] = []
                    for data in fro:
                        dict_pwo['ancestors'].append(data)
            except:
                pass

            list_pwo.append(dict_pwo)
        return(list_pwo)