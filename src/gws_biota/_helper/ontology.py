# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import re
from pronto import Ontology


class Onto():
    """
    This module allows to get all ontologie that will be used by the Gencovery web application.
    This include GO, SBO, BTO, CHEBI and ECO ontologies
    """

    ##################################################################
    ###################### FILE CORRECTION PART ######################
    ##################################################################

    # ECO (Evidence and Conclusion Ontology)
    @staticmethod
    def correction_of_eco_file(path, file):
        """
        Correct the initial eco.obo file which contained syntax errors which prevented to use
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

        with open(in_file, 'rt') as file:
            with open(out_file, 'wt') as outfile:
                for line in file.readlines():
                    if line.startswith('def: '):
                        label, definition = line.split("def: ", 1)
                        definition = re.sub(r'\[UniProt:[^\]]*\]', lambda x: x.group().replace(" ", "_"), definition)
                        outfile.write(f"{label}def: {definition}")
                    else:
                        outfile.write(line)

        return path, out_filename

    # SBO (Systems Biology Ontology)
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

        with open(in_file, 'rt') as file:
            with open(out_file, 'wt') as outfile:
                for line in file.readlines():
                    if not line.startswith('property_value'):
                        if line.startswith('synonym') and ' []' in line:
                            line = line.replace(' []', ' EXACT []')
                        outfile.write(line)

        return path, out_filename

    # PWO
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

        with open(in_file, 'rt') as file:
            with open(out_file, 'wt') as outfile:
                for line in file.readlines():
                    m = re.search('\[(.+)\]', line)
                    if m:
                        text = m.group(1)
                        entries = text.replace("\,", "##").split(",")
                        for i in range(0, len(entries)):
                            entries[i] = entries[i].strip().replace(" ", "-")

                        corrected_text = ", ".join(entries)
                        outfile.write(line.replace(text, corrected_text).replace("##", "\,"))
                    else:
                        outfile.write(line)

        return path, out_filename

    ##################################################################
    ##################### ONTHOLOGY CREATION PART ####################
    ##################################################################

    @staticmethod
    def create_ontology_from_file(path, file) -> Ontology:
        """
        This method allows the create an ontalogy from an obo file.

        :type file: str
        :param file: path of obo file
        :returns: Ontology object from the package pronto
        :rtype: Ontology
        """
        in_file = os.path.join(path, file)

        onto = Ontology(in_file)
        return onto

    ##################################################################
    ###################### FILE ANALYSIS PART ######################
    ##################################################################

    # BTO
    @staticmethod
    def parse_bto_from_ontology(ontology: Ontology):
        list_bto = []
        for term in ontology.terms():
            dict_ = {}
            if not term.name:
                continue
            # print(term.id)
            dict_['id'] = term.id
            dict_['name'] = term.name
            dict_['definition'] = str(term.definition)
            dict_['synonyms'] = []
            for syn in term.synonyms:
                dict_['synonyms'].append(str(syn.description))
            dict_['ancestors'] = [term.id]
            ancestors = term.superclasses(distance=1000, with_self=False)
            for sup in ancestors:
                dict_['ancestors'].append(sup.id)

            list_bto.append(dict_)

        return list_bto

    # OBO
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
            dict_go['name'] = term.name.replace('\r', '')
            dict_go['namespace'] = term.namespace.replace('\r', '')
            dict_go['definition'] = str(term.definition)  # str

            # ------ get xrefs ------#
            try:
                xrefs_fro = term.xrefs
                if len(xrefs_fro) > 0:
                    dict_go['xrefs'] = []
                    for data in xrefs_fro:
                        dict_go['xrefs'].append(data.id)
            except:
                pass

            # ------ get ancestors ------ #
            try:
                sup = term.superclasses(distance=1, with_self=False)
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
            # dict_go['synonyms'] = list(term.synonyms)

            list_alt_ids = list(term.alternate_ids)
            if len(list_alt_ids) > 0:
                dict_go['alt_id'] = list_alt_ids

            list_go.append(dict_go)

        return (list_go)

    # BTO
    @staticmethod
    def parse_bto_from_json(path, file):
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
                    dict_bto['name'] = data[key]['label']
                    if ('ancestors' in data[key].keys()):
                        dict_bto['ancestors'] = data[key]['ancestors']
                    if ('synonyms' in data[key].keys()):
                        dict_bto['synonyms'] = data[key]['synonyms']
                list_bto.append(dict_bto)

        return (list_bto)

    # ECO
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
            dict_eco['name'] = term.name.replace('\r', '')
            dict_eco['definition'] = str(term.definition)  # str

            try:
                sup = term.superclasses(distance=1, with_self=False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_eco['ancestors'] = []
                    for data in fro:
                        dict_eco['ancestors'].append(data)
            except:
                pass

            list_eco.append(dict_eco)
        return (list_eco)

    # SBO
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
            dict_sbo['name'] = term.name.replace('\r', '')

            try:
                sup = term.superclasses(distance=1, with_self=False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_sbo['ancestors'] = []
                    for data in fro:
                        dict_sbo['ancestors'].append(data)
            except:
                pass

            list_sbo.append(dict_sbo)

        return (list_sbo)

    # PWO
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
            dict_pwo['name'] = term.name.replace('\r', '')
            dict_pwo['definition'] = str(term.definition)  # str

            try:
                sup = term.superclasses(distance=1, with_self=False)
                fro = sup.to_set().ids
                if len(fro) > 0:
                    dict_pwo['ancestors'] = []
                    for data in fro:
                        dict_pwo['ancestors'].append(data)
            except:
                pass

            list_pwo.append(dict_pwo)
        return (list_pwo)

    # CHEBI
    @staticmethod
    def parse_chebi_from_ontology(ontology):
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
            subsets = ''
            if len(term.subsets):
                subsets = list(term.subsets)[0]

            dict_term = {}
            dict_term['id'] = term.id
            dict_term['name'] = term.name.replace('\r', '')
            dict_term['alt_id'] = list(term.alternate_ids)
            dict_term['subsets'] = subsets
            dict_term['ancestors'] = []
            dict_term['inchikey'] = None
            dict_term['inchi'] = None
            dict_term['smiles'] = None
            dict_term['formula'] = None
            dict_term['charge'] = None
            dict_term['mass'] = None
            dict_term['monoisotopic_mass'] = None

            for pv in term.annotations:
                if '/inchikey' in pv.property:
                    dict_term['inchikey'] = pv.literal
                elif '/inchi' in pv.property:
                    dict_term['inchi'] = pv.literal
                elif '/smiles' in pv.property:
                    dict_term['smiles'] = pv.literal
                elif '/formula' in pv.property:
                    dict_term['formula'] = pv.literal
                elif '/monoisotopicmass' in pv.property:
                    dict_term['monoisotopic_mass'] = pv.literal
                elif '/mass' in pv.property:
                    dict_term['mass'] = pv.literal
                elif '/charge' in pv.property:
                    dict_term['charge'] = pv.literal

            # ancestors
            for c in term.superclasses():
                if c.id != term.id:
                    dict_term['ancestors'].append(c.id)

            # synonyms
            dict_term['synonyms'] = []
            for syn in term.synonyms:
                if syn.scope == "EXACT":
                    if syn.description != dict_term['name']:
                        dict_term['synonyms'].append(syn.description)

            # definition
            if term.definition is None:
                dict_term['definition'] = ""
            else:
                dict_term['definition'] = term.definition

            dict_term['xref'] = {}
            for xref in term.xrefs:
                xref_id = xref.id.split(":")[0].lower()
                dict_term['xref'][xref_id] = xref.id.split(":")[1]

            list_chebi_term.append(dict_term)

        return (list_chebi_term)
