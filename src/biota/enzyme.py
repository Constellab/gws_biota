import os, sys
import asyncio
from biota.protein import Protein 
from biota.taxonomy import Taxonomy as Tax
from biota.bto import BTO as BT
from brenda.brenda import Brenda

from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Process, Model, ViewModel, ResourceViewModel, Resource, DbManager

from peewee import CharField, Model, chunked, ForeignKeyField, ManyToManyField, DeferredThroughModel
from peewee import IntegerField, FloatField
from peewee import Model as PWModel

import logging
from collections import OrderedDict
from brendapy import BrendaParser, BrendaProtein
from brendapy import utils
from brendapy.taxonomy import Taxonomy
from brendapy.tissues import BTO
from brendapy.substances import CHEBI

####################################################################################
#
# Enzyme class
#
####################################################################################
EnzymeBTODeffered = DeferredThroughModel()

class Enzyme(Protein):
    ec = CharField(null=True, index=True)
    organism = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Tax, backref = 'taxonomy', null = True)
    bto = ManyToManyField(BT, backref='blood tissue taxonomy', through_model = EnzymeBTODeffered)
    uniprot_id = CharField(null=True, index=True)
    _table_name = 'enzyme'

    #Setters
    def set_ec(self, ec__):
        self.ec = ec__
    
    def set_organism(self, organism__):
        self.organism = organism__

    def set_taxonomy(self):
        if(self.data['taxonomy'] != None):
            try:
                tax = Tax.get(Tax.tax_id == str(self.data['taxonomy']))
                self.taxonomy = tax
            except:
                print("did not found the tax_id: " + str(self.data['taxonomy']))
    
    def set_tissues(self):
        if(type(self.data['st']) == list):
            for i in range(0,len(self.data['st'])):
                try:
                    tissue = BT.get(BT.bto_id == self.data['st'][i])
                    self.bto.add(tissue)
                except:
                    print("BTO not found")
        else:
            try:
                tissue = BT.get(BT.bto_id == self.data['st'])
                self.bto.add(tissue)
            except:
                print("BTO not found")

    def set_uniprot_id(self, uniprot_id__):
        self.uniprot_id = uniprot_id__

    #Inserts
    def insert_protein_id(list__, key):
        for comp in list__:
            comp.set_protein_id(comp.data[key])

    def insert_ec(list__, key):
        for comp in list__:
            comp.set_ec(comp.data[key])

    def insert_organism(list__, key):
        for comp in list__:
            comp.set_organism(comp.data[key])
    """
    def insert_taxonomy(list__, key):
        for comp in list__:
            comp.set_taxonomy(comp.data[key])
    """

    def insert_uniprot_id(list__, key):
        for comp in list__:
            comp.set_uniprot_id(comp.data[key])
            
    @classmethod
    def create_enzymes_from_dict(cls, input_db_dir, **files):
        brenda = Brenda(os.path.join(input_db_dir, files['brenda_file']))
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
        cls.insert_ec(enzymes, 'ec')
        cls.insert_organism(enzymes, 'organism')
        cls.insert_uniprot_id(enzymes, 'uniprot')
        Controller.save_all()
        for enz in enzymes:
            enz.set_taxonomy()
            if('st' in enz.data.keys()):
                enz.set_tissues()
        return(list_dict)
    
    class Meta():
        table_name = 'enzymes'
    
class EnzymeBTO(PWModel):
    enzyme = ForeignKeyField(Enzyme)
    bto = ForeignKeyField(BT)
    class Meta:
        table_name = 'enzymes_btos'
        database = DbManager.db

class EnzymeJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"ec": {{view_model.model.ec}}, "organism": {{view_model.model.organism}}, "taxonomy": {{view_model.model.taxonomy}}, "bto": {{view_model.model.bto}}, "uniprot_id": {{view_model.model.uniprot_id}} }')


class EnzymeStatistics(Resource):
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
        
class process_statistics(Process):
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
        
            print('Extract total number of enzyme')
            enzymes = Enzyme.select()
            size = len(enzymes)
            se.set_total_number_enzyme(len(enzymes))

            print('Extract organisms by ec_group, references number, uniprots referenced number')

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
            
            print('Extraction of proportion of parameters referenced and number of entries in the table')
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
            
            print('Extract the proportion of the organism in the table')
            try:
                enzymes_organism = Enzyme.select().where(Enzyme.organism == params['organism'])
                proportion = (len(enzymes_organism)*100)/size
                se.set_proportion_in_table(str(proportion) + ' %')
            except:
                print("Organism " + params['organism'] + " not found in the table")

            
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
            
            print('Extraction of proportion of parameters referenced and number of entries in the table')
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
Controller.register_models([EnzymeStatistics, process_statistics])
