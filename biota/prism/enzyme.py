# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com
#
# BRENDA Copyright Notice and License:
# BRENDA data are available under the Creative Commons License (CC BY 4.0).
# The Creative Commons Attribution License CC BY 4.0 is applied to all copyrightable parts of BRENDA. 
# The copyrightable parts of BRENDA are copyright-protected by Prof. Dr. D. Schomburg, Technische 
# Universität Braunschweig, BRICS,Department of Bioinformatics and Biochemistry, 
# Rebenring 56, 38106 Braunschweig, Germany.
# https://www.brenda-enzymes.org
#
# Attribution 4.0 International (CC BY 4.0) information, 2020:
# You are free to:
#   * Share — copy and redistribute the material in any medium or format
#   * Adapt — remix, transform, and build upon the material
#     for any purpose, even commercially.
# This license is acceptable for Free Cultural Works.
# The licensor cannot revoke these freedoms as long as you follow the license terms
# (https://creativecommons.org/licenses/by/4.0/).

import os
from biota.prism.protein import Protein 
from biota.prism.taxonomy import Taxonomy as BiotaTaxo
from biota.prism.bto import BTO as BiotaBTO
from biota._helper.brenda import Brenda

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import Process, ResourceViewModel, Resource, DbManager

from peewee import CharField, ForeignKeyField, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel

EnzymeBTODeffered = DeferredThroughModel()

class Enzyme(Protein):
    """
    This class represents enzymes extracted from the BRENDA database.

    BRENDA is the main collection of enzyme functional data available to the scientific community 
    (https://www.brenda-enzymes.org/). BRENDA data are available under the Creative 
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.


    :property name : name of the compound
    :type name: class:`peewee.CharField`
    :property ec: ec accession number
    :type ec: class:`peewee.CharField`
    :property organism: organism of the enzyme
    :type organism: class:`peewee.CharField`
    :property taxonomy: taxonomy id that gives the organism
    :type taxonomy: class:`biota.db.Taxonomy`
    :property bto: bto id that gives the tissue location 
    :type bto: class:`biota.db.BTO`
    :property uniprot_id: uniprot id of the enzyme
    :type uniprot_id: class:`peewee.CharField`
    """
    
    name = CharField(null=True, index=True)
    ec = CharField(null=True, index=True)
    organism = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(BiotaTaxo, backref = 'enzymes', null = True)
    bto = ManyToManyField(BiotaBTO, backref='enzymes', through_model = EnzymeBTODeffered)
    uniprot_id = CharField(null=True, index=True)
    _table_name = 'enzyme'

    # -- C --

    @classmethod
    def create_enzyme_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `enzyme` database

        :param biodata_db_dir: path of the :file:`go.obo`
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """
        brenda = Brenda(os.path.join(biodata_db_dir, files['brenda_file']))
        list_proteins = brenda.parse_all_protein_to_dict()
        list_dict = []
        list_chemical_info = ['ac','cf','cr','en','exp','gs','ic50','in','lo','me','mw','nsp','os','oss',
        'pho','phr','phs','pi','pm','refs','sn','sy','su','to','tr','ts','tn','st','kkm','ki','km']
        for d in list_proteins:
            dict_enz = {}
            dict_enz['ec'] = d['ec']
            dict_enz['taxonomy'] = d['taxonomy']
            dict_enz['organism'] = d['organism']
            dict_enz['uniprot'] = d['uniprot']
            dict_enz['name'] = d['name']
            dict_enz['ec_group'] = d['ec_group']
            for info in list_chemical_info:
                if(info in d.keys()):
                    dict_enz[info]= d[info]
            list_dict.append(dict_enz)
        
        enzymes = [cls(data = dict_) for dict_ in list_dict]

        for enzyme in enzymes:
            enzyme.set_ec(enzyme.data["ec"])
            enzyme.set_name(enzyme.data["name"])
            enzyme.set_organism(enzyme.data["organism"])
            enzyme.set_uniprot_id(enzyme.data["uniprot"])

        cls.save_all(enzymes)

        with DbManager.db.atomic() as transaction :
            try:
                for enzyme in enzymes:
                    enzyme._update_taxonomy()
                    if 'st' in enzyme.data.keys():
                        enzyme._update_tissues()
        
                cls.save_all(enzymes)
            
            except:
                transaction.rollback()
                raise Exception("An error occured while setting enzyme taxonomy and bto")
        

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates tables related to enzyme entities such as enzymes, enzymes_btos
        Uses the super() method of the gws.model object
        """

        super().create_table(*args, **kwargs)
        EnzymeBTO = Enzyme.bto.get_through_model()
        EnzymeBTO.drop_table(*args, **kwargs)

    # -- D -- 

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops tables related to enzyme entities such as enzymes, enzymes_btos
        Uses the super() method of the gws.model object
        """
        EnzymeBTO = Enzyme.bto.get_through_model()
        EnzymeBTO.drop_table(*args, **kwargs)
        super().drop_table(*args, **kwargs)
    
    # -- S -- 

    def set_ec(self, ec):
        self.ec = ec
    
    def set_name(self, name):
        self.name = name

    def set_organism(self, organism):
        self.organism = organism
    
    def set_uniprot_id(self, uniprot_id):
        self.uniprot_id = uniprot_id

    # -- U --

    def _update_taxonomy(self):
        """
        See if there is any information about the enzyme taxonomy and if so, connects
            the enzyme and his taxonomy by adding the related tax_id from the taxonomy table
            to the taxonomy property of the enzyme
        """
        if(self.data['taxonomy'] != None):
            try:
                tax = BiotaTaxo.get(BiotaTaxo.tax_id == str(self.data['taxonomy']))
                self.taxonomy = tax
            except:
                pass
                #print("did not found the tax_id: " + str(self.data['taxonomy']))

    def _update_tissues(self):
        """
        See if there is any information about the enzyme tissue locations and if so, 
            connects the enzyme and tissues by adding an enzyme-tissues relation in th enzymes_btos
            table
        """
        if(type(self.data['st']) == list):
            for i in range(0,len(self.data['st'])):
                try:
                    tissue = BiotaBTO.get(BiotaBTO.bto_id == self.data['st'][i])
                    self.bto.add(tissue)
                except:
                    pass
                    #print("BTO not found")
        else:
            try:
                tissue = BiotaBTO.get(BiotaBTO.bto_id == self.data['st'])
                self.bto.add(tissue)
            except:
                pass
                #print("BTO not found")

    class Meta():
        table_name = 'enzyme'
    
class EnzymeBTO(PWModel):
    """
    This class refers to tissues of brenda enzymes
    EnzymeBTO entities are created by the _update_tissues() method of the Enzyme class

    :type enzyme: Enzyme 
    :property enzyme: id of the concerned enzyme
    :type bto: BTO 
    :property bto: tissue location
    """
    enzyme = ForeignKeyField(Enzyme)
    bto = ForeignKeyField(BiotaBTO)
    class Meta:
        table_name = 'enzymes_btos'
        database = DbManager.db

class EnzymeJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "ec": {{view_model.model.ec}},
            "organism": {{view_model.model.organism}},
            "name": {{view_model.model.data["name"]}},
            "taxonomy" : {{view_model.model.taxonomy}},
            "uniprot id": {{view_model.model.uniprot_id}}
            }
        """)

class EnzymeJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "ec": {{view_model.model.ec}},
            "organism": {{view_model.model.organism}},
            "name": {{view_model.model.data["name"]}},
            "taxonomy" : {{view_model.model.taxonomy}},
            "uniprot id": {{view_model.model.uniprot_id}},
            "bto ids": {{view_model.display_btos()}}
            "informative entries": {{view_model.display_entries()}}
            }
        """)
    
    def display_btos(self):
        q = EnzymeBTO.select().where(EnzymeBTO.enzyme == self.model.id)
        list_btos = []
        for i in range(0,len(q)):
            list_btos.append(q[i].bto.bto_id)
        return list_btos
    
    def display_entries(self):
        dict_entries = {}
        list_avoid = ["ec", "taxonomy", "name","organism", "uniprot", "st"]
        for key in self.model.data.keys():
            if(key not in list_avoid):
                dict_entries[key] = self.model.data[key]
        return dict_entries


class EnzymeStatistics(Resource):
    """
    This class refers to statistics of enzyme tables.
    The aim of this class is to gather statistics about enzymes in biota database.
    
    :property : number of enzymes by ec group
    :type enzymes_by_ec_group: dict
    :property number_of_ec_class: total number of ec class 
    :type number_of_ec_class: int
    :property number_of_entries: dictionnary where keys are a kinetic or chemical 
    information and values are number of enzyme with this parameter entered
    :type number_of_entries: dict
    :property set_number_of_organisms: total number of organism
    :type set_number_of_organisms: int
    :property proportion_by_ec_group: dictionnary that contains proportion (%) of enzymes 
    number by ec group in the table
    :type proportion_by_ec_group: dictionnary
    :property proportion_in_table: proportion of enzyme that refer to a specific organism in the table
    :type proportion_in_table: str 
    :property proportion_of_params: dictionnary where keys are a kinetic or chemical information 
    and values are proportion of enzyme with this parameter entered in the table
    :type proportion_of_params: dict
    :property total_number_of_enzyme: total number of enzyme in the table
    :type total_number_of_enzyme: int
    :property uniprots_referenced: total number of enzyme with a uniprot identifiers 
    referenced in the table
    :type uniprots_referenced: int
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {
            'enzymes_by_ec_group': 0,
            'number_of_ec_class': 0,
            'number_of_entries': 0,
            'number_of_organisms': 0,
            'number_of_references': 0,
            'organisms_by_ec_group': 0,
            'proportion_by_ec_group': 0,
            'proportion_in_table': 0,
            'proportion_of_params': 0,
            'total_number_of_enzyme': 0,
            'uniprots_referenced': 0     
        }
    
    #-------- Accessors --------#

    @property
    def enzymes_by_ec_group(self):
        return self.data['enzymes_by_ec_group']

    @property
    def number_of_ec_class(self):
        return self.data['number_of_ec_class']
    
    @property
    def number_of_entries(self):
        return self.data['number_of_entries']

    @property
    def number_of_organisms(self):
        return self.data['number_of_organisms']

    @property
    def number_of_references(self):
        return self.data['number_of_references']

    @property
    def organisms_by_ec_group(self):
        return self.data['organisms_by_ec_group']   

    @property
    def proportion_by_ec_group(self):
        return self.data['proportion_by_ec_group']

    @property
    def proportion_in_table(self):
        return self.data['proportion_in_table']

    @property
    def proportion_of_params(self):
        return self.data['proportion_of_params']

    @property
    def total_number_of_enzyme(self):
        return self.data['total_number_of_enzyme']
 
    @property
    def uniprots_referenced(self):
        return self.data['uniprots_referenced']
    
    #-------- Setters --------#

    def set_enzymes_by_ec_group(self, enzymes):
        self.data['enzymes_by_ec_group'] = enzymes
    
    def set_number_of_ec_class(self, classes):
        self.data['number_of_ec_class'] = classes
    
    def set_number_of_entries(self, uniprots):
        self.data['number_of_entries'] = uniprots
    
    def set_number_of_organisms(self, organisms):
        self.data['number_of_organisms'] = organisms
    
    def set_number_of_references(self, refs):
        self.data['number_of_references'] = refs
    
    def set_proportion_by_ec_group(self, proportions):
        self.data['proportion_by_ec_group'] = proportions
    
    def set_proportion_in_table(self, proportion):
        self.data['proportion_in_table'] = proportion
    
    def set_proportion_of_params(self, params):
        self.data['proportion_of_params'] = params
    
    def set_organisms_by_ec_group(self, organism):
        self.data['organisms_by_ec_group'] = organism

    def set_total_number_enzyme(self, number):
        self.data['total_number_of_enzyme'] = number

    def set_uniprots_referenced(self, uniprots):
        self.data['uniprots_referenced'] = uniprots

class EnzymeStatisticsJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{{view_model.model.data}}')
 
class EnzymeStatisticsProcess(Process):
    """
    The class allows the biota module to get statistics informations about enzymes in the biota database
    It browses enyme table to collect and process statistics informations
    
    The process can provide general statistics information about the table or more 
    specific informations with about enzymes of a given organism
    """
    input_specs = {'EnzymeStatistics': EnzymeStatistics}
    output_specs = {'EnzymeStatistics': EnzymeStatistics}
    async def task(self, params={}): 
        se = EnzymeStatistics()

        if (params['global_informations']): # Case if the user want only global information about the Enzyme table
            dict_entries = {}
            dict_enzymes_classes = {}
            dict_organisms = {}
            dict_organism_number_by_ec_group = {}
            dict_params = {}
            dict_proportion_ec_group = {}
            dict_references = {}
            dict_size_ec_group = {}
            list_infos = ['ac','cf','cl','cr','en','exp','gi','gs','ic50','in','lo','me','mw','nsp','os','oss',
        'pho','phr','phs','pi','pm','pu','ren','sa','sn','sy','su','to','tr','ts','st','kkm','ki','km','tn']
            proportions_params = {}
            uniprot_id_number = 0
        
            #print('Extract total number of enzyme')
            enzymes = Enzyme.select()
            size = len(enzymes)
            se.set_total_number_enzyme(len(enzymes))

            #print('Extract organisms by ec_group, references number, uniprots referenced number')

            for i in range(1,8):
                group = Enzyme.select().where(Enzyme.data['ec_group'] == str(i))
                dict_size_ec_group[i] = len(group)
                dict_group = {}
                for enzyme in group:

                    if(enzyme.organism not in dict_group.keys()):
                        dict_group[enzyme.organism] = 1
                    else:
                        dict_group[enzyme.organism] += 1

                    if(enzyme.organism not in dict_organisms.keys()):
                        dict_organisms[enzyme.organism] = 1
                    else:
                        dict_organisms[enzyme.organism] += 1

                    if(enzyme.ec not in dict_enzymes_classes.keys()):
                        dict_enzymes_classes[enzyme.ec] =1
                    else:
                        dict_enzymes_classes[enzyme.ec] += 1

                    if ('refs' in enzyme.data.keys()):
                        for j in range(0, len(enzyme.data['refs'])):
                            if(enzyme.data['refs'][j] not in dict_references.keys()):
                                dict_references[enzyme.data['refs'][j]] = 1
                            else:
                                dict_references[enzyme.data['refs'][j]] += 1

                    if(enzyme.uniprot_id):
                        uniprot_id_number += 1

                    dict_organism_number_by_ec_group[i] = len(dict_group)
                    dict_proportion_ec_group[i] = str(dict_size_ec_group[i]*100/size) + ' %'
            
            #print('Extraction of proportion of parameters referenced and number of entries in the table')
            for enzyme in enzymes:
                for i in range(0, len(list_infos)):
                    if (list_infos[i] in enzyme.data.keys()):
                        if (list_infos[i] not in dict_params.keys()):
                            dict_params[list_infos[i]] = 1
                            dict_entries[list_infos[i]] = 1
                        else:
                            dict_params[list_infos[i]] += 1
                            dict_entries[list_infos[i]] += 1

                        if(type(enzyme.data[list_infos[i]]) == list):
                            if(len(enzyme.data[list_infos[i]]) > 1):
                                for j in range(0, len(enzyme.data[list_infos[i]])-1):
                                    dict_entries[list_infos[i]] += 1
                        proportions_params[list_infos[i]] = str(dict_params[list_infos[i]]*100/len(enzymes)) + ' %'

            se.set_enzymes_by_ec_group(dict_size_ec_group)
            se.set_number_of_ec_class(len(dict_enzymes_classes))
            se.set_number_of_entries(dict_entries)
            se.set_number_of_organisms(len(dict_organisms))
            se.set_number_of_references(len(dict_references))
            se.set_organisms_by_ec_group(dict_organism_number_by_ec_group)
            se.set_proportion_by_ec_group(dict_proportion_ec_group)
            se.set_proportion_of_params(proportions_params)
            se.set_uniprots_referenced(uniprot_id_number)
                    
        else: # Case if the user want informations about an organism
            dict_entries = {}
            dict_enzymes_classes = {}
            dict_organism_number_by_ec_group = {}
            dict_params = {}
            dict_proportion_ec_group = {}
            proportions_params = {}
            dict_references = {}
            dict_size_ec_group = {}
            list_infos = ['ac','cf','cr','en','exp','gs','ic50','in','lo','me','mw','nsp','os','oss',
                    'pho','phr','phs','pi','pm','sn','sy','su','to','tr','ts','st','kkm','ki','km','tn']
            size = len(Enzyme.select())
            uniprot_id_number = 0
            
            #print('Extract the proportion of the organism in the table')
            try:
                enzymes_organism = Enzyme.select().where(Enzyme.organism == params['organism'])
                proportion = (len(enzymes_organism)*100)/size
                se.set_proportion_in_table(str(proportion) + ' %')
            except:
                pass
                #print("Organism " + params['organism'] + " not found in the table")

            
            for i in range(1,8):
                group = Enzyme.select().where((Enzyme.organism == params['organism']) & (Enzyme.data['ec_group'] == str(i)))
                dict_size_ec_group[i] = len(group)
                dict_proportion_ec_group[i] = ''
                for enzyme in group:
                    if(enzyme.ec not in dict_enzymes_classes.keys()):
                        dict_enzymes_classes[enzyme.ec] =1
                    else:
                        dict_enzymes_classes[enzyme.ec] += 1
                    
                    if ('refs' in enzyme.data.keys()):
                        for j in range(0, len(enzyme.data['refs'])):
                            if(enzyme.data['refs'][j] not in dict_references.keys()):
                                dict_references[enzyme.data['refs'][j]] = 1
                            else:
                                dict_references[enzyme.data['refs'][j]] += 1

                    if(enzyme.uniprot_id):
                        uniprot_id_number += 1
                    
                    if(proportion):
                        dict_proportion_ec_group[i] = str(dict_size_ec_group[i]*100/len(enzymes_organism)) + ' %'
            
            #print('Extraction of proportion of parameters referenced and number of entries in the table')
            for enzyme in enzymes_organism:
                for i in range(0, len(list_infos)):
                    if (list_infos[i] in enzyme.data.keys()):
                        if (list_infos[i] not in dict_params.keys()):
                            dict_params[list_infos[i]] = 1
                            dict_entries[list_infos[i]] = 1
                        else:
                            dict_params[list_infos[i]] += 1
                            dict_entries[list_infos[i]] += 1

                        if(type(enzyme.data[list_infos[i]]) == list):
                            if(len(enzyme.data[list_infos[i]]) > 1):
                                for j in range(0, len(enzyme.data[list_infos[i]])-1):
                                    dict_entries[list_infos[i]] += 1
                        proportions_params[list_infos[i]] = str(dict_params[list_infos[i]]*100/len(enzymes_organism)) + ' %'

            
            se.set_enzymes_by_ec_group(dict_size_ec_group)
            se.set_number_of_ec_class(len(dict_enzymes_classes))
            se.set_number_of_entries(dict_entries)
            se.set_number_of_references(len(dict_references))
            se.set_proportion_by_ec_group(dict_proportion_ec_group)
            se.set_proportion_of_params(proportions_params)
            se.set_total_number_enzyme(len(enzymes_organism))
            se.set_uniprots_referenced(uniprot_id_number) 

        self.output['EnzymeStatistics'] = se

EnzymeBTODeffered.set_model(EnzymeBTO)

Controller.register_model_classes([Enzyme, EnzymeStatistics, EnzymeStatisticsProcess])
