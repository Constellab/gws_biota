# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from biota.db.protein import Protein 
from biota.db.taxonomy import Taxonomy as BiotaTaxo
from biota.db.bto import BTO as BiotaBTO
from biota._helper.brenda import Brenda

from peewee import CharField, ForeignKeyField, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import Process, ResourceViewModel, Resource, DbManager

from biota.db.enzyme import Enzyme
from biota.db.protein import Protein

EnzymeFunctionBTODeffered = DeferredThroughModel()

"""
BRENDA ENZYME information from flat file.
The following information is available:
    AC    activating compound
    AP    application
    CF    cofactor
    CL    cloned
    CR    crystallization
    EN    engineering
    EXP    expression
    GI    general information on enzyme
    GS    general stability
    IC50    IC-50 Value
    ID    EC-class
    IN    inhibitors
    KKM    Kcat/KM-Value substrate in {...}
    KI    Ki-value    inhibitor in {...}
    KM    KM-value    substrate in {...}
    LO    localization
    ME    metals/ions
    MW    molecular weight
    NSP    natural substrates/products    reversibilty information in {...}
    OS    oxygen stability
    OSS    organic solvent stability
    PHO    pH-optimum
    PHR    pH-range
    PHS    pH stability
    PI    isoelectric point
    PM    posttranslation modification
    PR    protein
    PU    purification
    RE    reaction catalyzed
    RF    references
    REN    renatured
    RN    accepted name (IUPAC)
    RT    reaction type
    SA    specific activity
    SN    synonyms
    SP    substrates/products    reversibilty information in {...}
    SS    storage stability
    ST    source/tissue
    SU    subunits
    SY    systematic name
    TN    turnover number    substrate in {...}
    TO    temperature optimum
    TR    temperature range
    TS    temperature stability
"""

class EnzymeFunction(Resource):
    """
    This class represents enzyme_functions extracted from the BRENDA and BKMS database.

    BRENDA is the main collection of enzyme functional data available to the scientific community 
    (https://www.brenda-enzymes.org/). BRENDA data are available under the Creative 
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    BKMS-react is an integrated and non-redundant biochemical reaction database 
    containing known enzyme-catalyzed and spontaneous reactions. 
    Biochemical reactions collected from BRENDA, KEGG, MetaCyc and 
    SABIO-RK were matched and integrated by aligning substrates and products.

    :property go_id : GO term id
    :type go_id : class:`peewee.CharField`
    :property name: name of the compound
    :type name: class:`peewee.CharField`
    :property ec: ec accession number
    :type ec: class:`peewee.CharField`
    :property taxonomy: taxonomy id that gives the organism
    :type taxonomy: class:`biota.db.Taxonomy`
    :property bto: bto id that gives the tissue location 
    :type bto: class:`biota.db.BTO`
    :property uniprot_id: uniprot id of the enzyme
    :type uniprot_id: class:`peewee.CharField`
    """
    
    go_id = CharField(null=True, index=True)
    enzyme = ForeignKeyField(Enzyme, backref = '', null = True)
    taxonomy = ForeignKeyField(BiotaTaxo, backref = 'enzyme_functions', null = True)
    bto = ManyToManyField(BiotaBTO, backref='enzyme_functions', through_model = EnzymeFunctionBTODeffered)
    _table_name = 'enzyme_function'

    # -- C --

    @classmethod
    def create_enzyme_function_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `enzyme_function` database

        :param biodata_db_dir: path of the :file:`go.obo`
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """
        brenda = Brenda(os.path.join(biodata_db_dir, files['brenda_file']))
        list_of_proteins = brenda.parse_all_protein_to_dict()
        list_of_chemical_info = ['ac','cf','cr','en','exp','gs','ic50','in','lo','me','mw','nsp','os','oss',
        'pho','phr','phs','pi','pm','refs','sn','sy','su','to','tr','ts','tn','st','kkm','ki','km']
        
        proteins = {}
        enzymes = {}
        for d in list_of_proteins:
            ec = d['ec']

            if ec in enzymes:
                continue
                
            protein = Protein(
                name = d['name'], 
                uniprot_id = d['uniprot'], 
                data = {'source': 'brenda'}
            )

            enzyme = Enzyme(
                ec = ec, 
                protein = protein,
            )     

            proteins[ec] = protein
            enzymes[ec] = enzyme

        Protein.save_all(proteins.values()) 
        Enzyme.save_all(enzymes.values())

        enzyme_functions = []
        for d in list_of_proteins:
            ec = d['ec']
            enz_fun_data = {}
            enz_fun_data['taxonomy'] = d['taxonomy']
            enz_fun_data['organism'] = d['organism']
            for info in list_of_chemical_info:
                if(info in d.keys()):
                    enz_fun_data[info]= d[info]

            enz_fun = EnzymeFunction(
                enzyme = enzymes[ec],
                data = enz_fun_data
            )

            enzyme_functions.append(enz_fun)

        cls.save_all(enzyme_functions)

        with DbManager.db.atomic() as transaction :
            try:
                for enzyme_function in enzyme_functions:
                    enzyme_function._update_taxonomy()
                    if 'st' in enzyme_function.data.keys():
                        enzyme_function._update_tissues()
        
                cls.save_all(enzyme_functions)
            
            except:
                transaction.rollback()
                raise Exception("An error occured while setting enzyme_function taxonomy and bto")
        

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `enzyme_function` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        Protein.create_table(*args, **kwargs)
        Enzyme.create_table(*args, **kwargs)

        super().create_table(*args, **kwargs)
        EnzymeFunctionBTO = EnzymeFunction.bto.get_through_model()
        EnzymeFunctionBTO.drop_table(*args, **kwargs)

    # -- D -- 

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops `enzyme_function` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        EnzymeFunctionBTO = EnzymeFunction.bto.get_through_model()
        EnzymeFunctionBTO.drop_table(*args, **kwargs)
        super().drop_table(*args, **kwargs)
    
    # -- E --

    @property
    def ec(self) -> str:
        """
        EC number of the enzyme

        :returns: The EC number of the enzyme
        :rtype: str
        """
        return str(self.enzyme.ec)
    
    # -- N --

    @property
    def name(self):
        """
        Name of the enzyme

        :returns: The name of the enzyme
        :rtype: str
        """
        return str(self.enzyme.name)

    # -- O --

    @property
    def organism(self):
        """
        Name of the organism

        :returns: The name of the organism associated to the enzyme function
        :rtype: str
        """
        return self.data["organism"]

    # -- U --

    def _update_taxonomy(self):
        """
        See if there is any information about the enzyme_function taxonomy and if so, connects
            the enzyme_function and its taxonomy by adding the related tax_id from the taxonomy table
            to the taxonomy property of the enzyme_function
        """
        if(self.data['taxonomy'] != None):
            try:
                tax = BiotaTaxo.get(BiotaTaxo.tax_id == str(self.data['taxonomy']))
                self.taxonomy = tax
            except:
                pass

    def _update_tissues(self):
        """
        See if there is any information about the enzyme_function tissue locations and if so, 
            connects the enzyme_function and tissues by adding an enzyme_function-tissues relation in th enzymes_btos
            table
        """
        if(type(self.data['st']) == list):
            for i in range(0,len(self.data['st'])):
                try:
                    tissue = BiotaBTO.get(BiotaBTO.bto_id == self.data['st'][i])
                    self.bto.add(tissue)
                except:
                    pass
        else:
            try:
                tissue = BiotaBTO.get(BiotaBTO.bto_id == self.data['st'])
                self.bto.add(tissue)
            except:
                pass

    class Meta():
        table_name = 'enzyme_function'
    
class EnzymeFunctionBTO(PWModel):
    """
    This class refers to tissues of brenda enzyme_functions
    EnzymeFunctionBTO entities are created by the _update_tissues() method of the EnzymeFunction class

    :type enzyme_function: EnzymeFunction 
    :property enzyme_function: id of the concerned enzyme_function
    :type bto: BTO 
    :property bto: tissue location
    """
    enzyme_function = ForeignKeyField(EnzymeFunction)
    bto = ForeignKeyField(BiotaBTO)
    class Meta:
        table_name = 'enzymes_btos'
        database = DbManager.db

class EnzymeFunctionStatistics(Resource):
    """
    This class refers to statistics of enzyme_function tables.
    The aim of this class is to gather statistics about enzyme_functions in biota database.
    
    :property : number of enzyme_functions by ec group
    :type enzyme_functions_by_ec_group: dict
    :property number_of_ec_class: total number of ec class 
    :type number_of_ec_class: int
    :property number_of_entries: dictionnary where keys are a kinetic or chemical 
    information and values are number of enzyme_function with this parameter entered
    :type number_of_entries: dict
    :property set_number_of_organisms: total number of organism
    :type set_number_of_organisms: int
    :property proportion_by_ec_group: dictionnary that contains proportion (%) of enzyme_functions 
    number by ec group in the table
    :type proportion_by_ec_group: dictionnary
    :property proportion_in_table: proportion of enzyme_function that refer to a specific organism in the table
    :type proportion_in_table: str 
    :property proportion_of_params: dictionnary where keys are a kinetic or chemical information 
    and values are proportion of enzyme_function with this parameter entered in the table
    :type proportion_of_params: dict
    :property enzyme_function_count: total number of enzyme_function in the table
    :type enzyme_function_count: int
    :property uniprots_referenced: total number of enzyme_function with a uniprot identifiers 
    referenced in the table
    :type uniprots_referenced: int
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {
            'enzyme_functions_by_ec_group': 0,
            'number_of_ec_class': 0,
            'number_of_entries': 0,
            'number_of_organisms': 0,
            'number_of_references': 0,
            'organisms_by_ec_group': 0,
            'proportion_by_ec_group': 0,
            'proportion_in_table': 0,
            'proportion_of_params': 0,
            'enzyme_function_count': 0,
            'uniprots_referenced': 0     
        }
    
    #-------- Accessors --------#

    @property
    def enzyme_functions_by_ec_group(self):
        return self.data['enzyme_functions_by_ec_group']

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
    def enzyme_function_count(self):
        return self.data['enzyme_function_count']
 
    @property
    def uniprots_referenced(self):
        return self.data['uniprots_referenced']
    
    #-------- Setters --------#

    def set_enzyme_functions_by_ec_group(self, enzyme_functions):
        self.data['enzyme_functions_by_ec_group'] = enzyme_functions
    
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

    def set_enzyme_function_count(self, number):
        self.data['enzyme_function_count'] = number

    def set_uniprots_referenced(self, uniprots):
        self.data['uniprots_referenced'] = uniprots

class EnzymeFunctionStatisticsJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{{view_model.model.data}}')
 
class EnzymeFunctionStatisticsProcess(Process):
    """
    The class allows the biota module to get statistics informations about enzyme_functions in the biota database
    It browses enyme table to collect and process statistics informations
    
    The process can provide general statistics information about the table or more 
    specific informations with about enzyme_functions of a given organism
    """
    input_specs = {'EnzymeFunctionStatistics': EnzymeFunctionStatistics}
    output_specs = {'EnzymeFunctionStatistics': EnzymeFunctionStatistics}
    async def task(self, params={}): 
        se = EnzymeFunctionStatistics()

        if (params['global_informations']): # Case if the user want only global information about the EnzymeFunction table
            dict_entries = {}
            dict_enz_funyme_functions_classes = {}
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
        
            #print('Extract total number of enzyme_function')
            enzyme_functions = EnzymeFunction.select()
            size = len(enzyme_functions)
            se.set_enzyme_function_count(len(enzyme_functions))

            #print('Extract organisms by ec_group, references number, uniprots referenced number')

            for i in range(1,8):
                group = EnzymeFunction.select().where(EnzymeFunction.data['ec_group'] == str(i))
                dict_size_ec_group[i] = len(group)
                dict_group = {}
                for enzyme_function in group:

                    if(enzyme_function.organism not in dict_group.keys()):
                        dict_group[enzyme_function.organism] = 1
                    else:
                        dict_group[enzyme_function.organism] += 1

                    if(enzyme_function.organism not in dict_organisms.keys()):
                        dict_organisms[enzyme_function.organism] = 1
                    else:
                        dict_organisms[enzyme_function.organism] += 1

                    if(enzyme_function.ec not in dict_enz_funyme_functions_classes.keys()):
                        dict_enz_funyme_functions_classes[enzyme_function.ec] =1
                    else:
                        dict_enz_funyme_functions_classes[enzyme_function.ec] += 1

                    if ('refs' in enzyme_function.data.keys()):
                        for j in range(0, len(enzyme_function.data['refs'])):
                            if(enzyme_function.data['refs'][j] not in dict_references.keys()):
                                dict_references[enzyme_function.data['refs'][j]] = 1
                            else:
                                dict_references[enzyme_function.data['refs'][j]] += 1

                    if(enzyme_function.uniprot_id):
                        uniprot_id_number += 1

                    dict_organism_number_by_ec_group[i] = len(dict_group)
                    dict_proportion_ec_group[i] = str(dict_size_ec_group[i]*100/size) + ' %'
            
            #print('Extraction of proportion of parameters referenced and number of entries in the table')
            for enzyme_function in enzyme_functions:
                for i in range(0, len(list_infos)):
                    if (list_infos[i] in enzyme_function.data.keys()):
                        if (list_infos[i] not in dict_params.keys()):
                            dict_params[list_infos[i]] = 1
                            dict_entries[list_infos[i]] = 1
                        else:
                            dict_params[list_infos[i]] += 1
                            dict_entries[list_infos[i]] += 1

                        if(type(enzyme_function.data[list_infos[i]]) == list):
                            if(len(enzyme_function.data[list_infos[i]]) > 1):
                                for j in range(0, len(enzyme_function.data[list_infos[i]])-1):
                                    dict_entries[list_infos[i]] += 1
                        proportions_params[list_infos[i]] = str(dict_params[list_infos[i]]*100/len(enzyme_functions)) + ' %'

            se.set_enzyme_functions_by_ec_group(dict_size_ec_group)
            se.set_number_of_ec_class(len(dict_enz_funyme_functions_classes))
            se.set_number_of_entries(dict_entries)
            se.set_number_of_organisms(len(dict_organisms))
            se.set_number_of_references(len(dict_references))
            se.set_organisms_by_ec_group(dict_organism_number_by_ec_group)
            se.set_proportion_by_ec_group(dict_proportion_ec_group)
            se.set_proportion_of_params(proportions_params)
            se.set_uniprots_referenced(uniprot_id_number)
                    
        else: # Case if the user want informations about an organism
            dict_entries = {}
            dict_enz_funyme_functions_classes = {}
            dict_organism_number_by_ec_group = {}
            dict_params = {}
            dict_proportion_ec_group = {}
            proportions_params = {}
            dict_references = {}
            dict_size_ec_group = {}
            list_infos = ['ac','cf','cr','en','exp','gs','ic50','in','lo','me','mw','nsp','os','oss',
                    'pho','phr','phs','pi','pm','sn','sy','su','to','tr','ts','st','kkm','ki','km','tn']
            size = len(EnzymeFunction.select())
            uniprot_id_number = 0
            
            #print('Extract the proportion of the organism in the table')
            try:
                enzymes_organism = EnzymeFunction.select().where(EnzymeFunction.organism == params['organism'])
                proportion = (len(enzymes_organism)*100)/size
                se.set_proportion_in_table(str(proportion) + ' %')
            except:
                pass
                #print("Organism " + params['organism'] + " not found in the table")

            
            for i in range(1,8):
                group = EnzymeFunction.select().where((EnzymeFunction.organism == params['organism']) & (EnzymeFunction.data['ec_group'] == str(i)))
                dict_size_ec_group[i] = len(group)
                dict_proportion_ec_group[i] = ''
                for enzyme_function in group:
                    if(enzyme_function.ec not in dict_enz_funyme_functions_classes.keys()):
                        dict_enz_funyme_functions_classes[enzyme_function.ec] =1
                    else:
                        dict_enz_funyme_functions_classes[enzyme_function.ec] += 1
                    
                    if ('refs' in enzyme_function.data.keys()):
                        for j in range(0, len(enzyme_function.data['refs'])):
                            if(enzyme_function.data['refs'][j] not in dict_references.keys()):
                                dict_references[enzyme_function.data['refs'][j]] = 1
                            else:
                                dict_references[enzyme_function.data['refs'][j]] += 1

                    if(enzyme_function.uniprot_id):
                        uniprot_id_number += 1
                    
                    if(proportion):
                        dict_proportion_ec_group[i] = str(dict_size_ec_group[i]*100/len(enzymes_organism)) + ' %'
            
            #print('Extraction of proportion of parameters referenced and number of entries in the table')
            for enzyme_function in enzymes_organism:
                for i in range(0, len(list_infos)):
                    if (list_infos[i] in enzyme_function.data.keys()):
                        if (list_infos[i] not in dict_params.keys()):
                            dict_params[list_infos[i]] = 1
                            dict_entries[list_infos[i]] = 1
                        else:
                            dict_params[list_infos[i]] += 1
                            dict_entries[list_infos[i]] += 1

                        if(type(enzyme_function.data[list_infos[i]]) == list):
                            if(len(enzyme_function.data[list_infos[i]]) > 1):
                                for j in range(0, len(enzyme_function.data[list_infos[i]])-1):
                                    dict_entries[list_infos[i]] += 1
                        proportions_params[list_infos[i]] = str(dict_params[list_infos[i]]*100/len(enzymes_organism)) + ' %'

            
            se.set_enzyme_functions_by_ec_group(dict_size_ec_group)
            se.set_number_of_ec_class(len(dict_enz_funyme_functions_classes))
            se.set_number_of_entries(dict_entries)
            se.set_number_of_references(len(dict_references))
            se.set_proportion_by_ec_group(dict_proportion_ec_group)
            se.set_proportion_of_params(proportions_params)
            se.set_enzyme_function_count(len(enzymes_organism))
            se.set_uniprots_referenced(uniprot_id_number) 

        self.output['EnzymeFunctionStatistics'] = se

EnzymeFunctionBTODeffered.set_model(EnzymeFunctionBTO)

Controller.register_model_classes([EnzymeFunction, EnzymeFunctionStatistics, EnzymeFunctionStatisticsProcess])