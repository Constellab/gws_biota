# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from collections import OrderedDict

from peewee import CharField, ForeignKeyField, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel

from gws.controller import Controller
from gws.model import Config, Process, Resource

from biota.db.base import Base, DbManager
from biota.db.taxonomy import Taxonomy as BiotaTaxo
from biota.db.po import PO
from biota.db.bto import BTO as BiotaBTO
from biota.db.fasta import Fasta


EnzymeBTODeffered = DeferredThroughModel()

class Param():
    """
    Adpater class that represents a BRENDA parameter

    :property what : Description of the parameter
    :type what : srt
    :property value : Value of the parameter
    :type value : srt
    :property refs : References numbers associated with the parameter value
    :type refs : list
    :property full_refs : Full references (pubmed id, or description) associated with the parameter value
    :type full_refs : list
    :property comments : Short comments extracted from the references 
    :type comments : str
    """

    what: str = None
    data: dict = None
    refs: list = []
    full_refs: list = []
    comments: str = None

    def __init__(self, data = None, refs = None, full_refs = None, comments = None, what = None):
        self.data = data
        self.refs = refs
        self.full_refs = full_refs
        self.comments = comments
        self.what = what

    @property
    def value(self):
        if self.data is None:
            return None
        else:
            return self.data.get("data", None)

    def exists(self) -> bool:
        """
        Returns True if the parameter exists (i.e. :property:`value` is not `None`) 
        and False otherwise.
        
        :rtype: bool
        """
        return not self.value is None
    
    def get(self, key):
        return self.data.get(key, None)

class Params():
    """
    Adpater class that represents a list of BRENDA parameters
    """

    _name = None
    _data = None
    _full_refs = None

    __whats = dict(
        AC = "activating compound",
        AP = "application",
        CF = "cofactor",
        CL = "cloned",
        CR = "crystallization",
        EN = "engineering",
        EXP = "expression",
        GI = "general information on enzyme",
        GS = "general stability",
        IC50 = "IC-50 Value",
        ID = "EC-class",
        IN = "inhibitors",
        KKM = "Kcat/KM-Value substrate in {...}",
        KI = "Ki-value    inhibitor in {...}",
        KM = "KM-value    substrate in {...}",
        LO = "localization",
        ME = "metals/ions",
        MW = "molecular weight",
        NSP = "natural substrates/products    reversibilty information in {...}",
        OS = "oxygen stability",
        OSS = "organic solvent stability",
        PHO = "pH-optimum",
        PHR = "pH-range",
        PHS = "pH stability",
        PI = "isoelectric point",
        PM = "posttranslation modification",
        PR = "protein",
        PU = "purification",
        RE = "reaction catalyzed",
        RF = "references",
        REN = "renatured",
        RN = "accepted name (IUPAC)",
        RT = "reaction type",
        SA = "specific activity",
        SN = "synonyms",
        SP = "substrates/products    reversibilty information in {...}",
        SS = "storage stability",
        ST = "source/tissue",
        SU = "subunits",
        SY = "systematic name",
        TN = "turnover number substrate in {...}",
        TO = "temperature optimum",
        TR = "temperature range",
        TS = "temperature stability"
    )
    
    def __init__(self, name, data):
        self._name = name
        self._data = data.get(name, None)
        self._full_refs = data.get("references", None)
        
    # -- G --

    def __len__(self):
        if isinstance(self._data, list):
            return len(self._data)
        else:
            return 0

    def __getitem__(self, index = 0):
        if isinstance(self._data, list):
            if index < len(self):
                if isinstance(self._data[index], str):
                    return Param(
                        data = {'data': self._data[index]},
                        what = self.__whats[self._name]
                    )
                elif isinstance(self._data[index], dict):
                    return Param(
                        data = self._data[index],
                        refs = self._data[index].get("refs", None),
                        full_refs = self._full_refs,
                        comments = self._data[index].get("comment", None),
                        what = self.__whats[self._name]
                    )
                else:
                    return Param()    
            else:
                return Param()
        else:
            return Param()

    def __str__(self):
        """String representation. """
        from pprint import pformat
        return pformat({
            "name" : self._name,
            "data" : self._data,
            "full_refs" : self._full_refs
        })

class Enzyme(Base):
    """
    This class represents enzymes extracted from open databases

    * Uniprot:

    * Brenda:
        BRENDA is the main collection of enzyme functional data available to the scientific community 
        (https://www.brenda-enzymes.org/). BRENDA data are available under the Creative 
        Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    * BKMS:
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
    
    po = ForeignKeyField(PO, backref = 'enzymes', null = True)
    ec_number = CharField(null=True, index=True)
    uniprot_id = CharField(null=True, index=True)
    tax_id = CharField(null=True, index=True)
    bto = ManyToManyField(BiotaBTO, through_model = EnzymeBTODeffered)
    
    _fts_fields = { **Base._fts_fields, 'RN': 2.0, 'organism': 1.0 }
    _table_name = 'enzymes'

    # -- C --

    @classmethod
    def create_enzyme_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `enzyme` database

        :param biodata_dir: path of the :file:`go.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.brenda import Brenda
        from biota._helper.bkms import BKMS

        job = kwargs.get('job',None)
        brenda = Brenda(os.path.join(biodata_dir, kwargs['brenda_file']))
        list_of_enzymes = brenda.parse_all_enzyme_to_dict()

        po_list = {}
        enzymes = []
        for d in list_of_enzymes:
            ec = d['ec']
            enz = Enzyme(
                ec_number = ec,
                uniprot_id = d["uniprot"],
                data = d
            )

            if not ec in po_list:
                po_list[ec] = PO(
                    name = d["RN"][0],
                    ec_number = ec,
                )

            if not job is None:
                enz._set_job(job)
                po_list[ec]._set_job(job)

            #del d["RN"]
            del d["protein_id"]
            del d["ec"]
            del d["uniprot"]

            enzymes.append(enz)

        PO.save_all(po_list.values())
        cls.save_all(enzymes)
        cls.__update_tax_tissue(enzymes)  

        if 'bkms_file' in kwargs:
            from biota._helper.bkms import BKMS
            list_of_bkms = BKMS.parse_csv_from_file(biodata_dir, kwargs['bkms_file'])
            cls.__update_pathway_from_bkms(list_of_bkms)
    
    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `enzyme` table and related tables.

        Extra parameters are passed to :meth:`create_table`
        """
        PO.create_table()

        super().create_table(*args, **kwargs)
        EnzymeBTO.create_table()

        #raise Exception("A")

    # -- D -- 

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        #EnzymeBTO = Enzyme.bto.get_through_model()
        EnzymeBTO.drop_table(*args, **kwargs)
        super().drop_table(*args, **kwargs)
    
    # -- F --
    
    def fasta(self):
        try:
            return Fasta.get(Fasta.uniprot_id == self.uniprot_id)
        except:
            return None

    # -- N --

    @property
    def name(self):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme orthologue
        :rtype: str
        """
        return self.po.get_name()

    @property
    def synomyms(self):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme orthologue
        :rtype: str
        """
        return self.po.synonyms

    # -- O --

    @property
    def organism(self):
        """
        Name of the organism

        :returns: The name of the organism associated to the enzyme function
        :rtype: str
        """
        return self.data["organism"]

    # -- P --

    def params(self, name) -> Params:
        """
        Returns the list of parameters associated with `name`

        :param name: Name of the parameter
        :type name: str
        :returns: Parameters
        :rtype: ParamList
        """
        return Params(name, self.data)

    # -- R --

    @property
    def reactions(self):
        """
        Returns the list of reactions associated with the enzyme function
        :returns: List of reactions
        :rtype: Query rows
        """
        from biota.db.reaction import Reaction, ReactionEnzyme
        from peewee import JOIN
        Q = Reaction.select() \
                    .join(ReactionEnzyme) \
                    .where(ReactionEnzyme.enzyme == self)        
        return Q

    # -- S --

    def save(self, *arg, **kwargs):
        if isinstance(self.data, OrderedDict):
            self.data = dict(self.data)
        
        return super().save(*arg, **kwargs)

    # -- T --

    @property
    def taxonomy(self):
        try:
            return BiotaTaxo.get(BiotaTaxo.tax_id == self.tax_id)
        except:
            return None

    # -- U --

    @classmethod
    def __update_tax_tissue(cls, enzymes):

        for enz in enzymes:
            enz.__update_taxonomy()
            enz.__update_tissues()

        cls.save_all(enzymes)

    def __update_taxonomy(self):
        """
        See if there is any information about the enzyme taxonomy and if so, connects
        the enzyme and its taxonomy by adding the related tax_id from the taxonomy 
        table to the taxonomy property of the enzyme
        """

        if 'taxonomy' in self.data:
            try:
                #tax = BiotaTaxo.get(BiotaTaxo.tax_id == str(self.data['taxonomy']))
                self.tax_id = str(self.data['taxonomy'])
                del self.data['taxonomy']
            except:
                pass

    def __update_tissues(self):
        """
        See if there is any information about the enzyme tissue locations and if so, 
        connects the enzyme and tissues by adding an enzyme-tissues relation 
        in the enzyme_btos table
        """

        n = len(self.params('ST'))
        bto_ids = []
        for i in range(0,n):
            bto_ids.append( self.params('ST')[i].get("bto") )
            
        Q = BiotaBTO.select().where(BiotaBTO.bto_id << bto_ids)
        for bto in Q: 
            self.bto.add(bto)

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the enzyme tissue locations and if so, 
        connects the enzyme and tissues by adding an enzyme-tissues relation 
        in the enzyme_btostable
        """

        po_list = {}
        bulk_size = 750
        dbs = ['brenda', 'kegg', 'metacyc']
        for bkms in list_of_bkms:
            ec_number = bkms["ec_number"]
    
            Q = PO.select().where(PO.ec_number == ec_number)
            for enzyme in Q:
                for k in dbs:

                    if bkms.get(k+'_pathway_name',"") != "":
                        pwy_id = bkms.get(k+'_pathway_id', "ID")
                        pwy_name = bkms[k+'_pathway_name']
                        enzyme.data[k+'_pathway'] = { pwy_id : pwy_name }

                po_list[enzyme.ec_number] = enzyme

                if len(po_list.keys()) >= bulk_size:
                    PO.save_all(po_list.values())
                    po_list = []

        if len(po_list) > 0:
            PO.save_all(po_list.values())


class EnzymeBTO(PWModel):
    """
    This class refers to tissues of brenda enzymes
    EnzymeBTO entities are created by the __update_tissues() method of the Enzyme class

    :type enzyme: Enzyme 
    :property enzyme: id of the concerned enzyme
    :type bto: BTO 
    :property bto: tissue location
    """
    enzyme = ForeignKeyField(Enzyme)
    bto = ForeignKeyField(BiotaBTO)

    class Meta:
         table_name = 'enzyme_btos'
         database = DbManager.db
        
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
    :property enzyme_count: total number of enzyme in the table
    :type enzyme_count: int
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
            'enzyme_count': 0,
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
    def enzyme_count(self):
        return self.data['enzyme_count']
 
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

    def set_enzyme_count(self, number):
        self.data['enzyme_count'] = number

    def set_uniprots_referenced(self, uniprots):
        self.data['uniprots_referenced'] = uniprots

class StatisticsExtractor(Process):
    """
    The class allows the biota module to get statistics informations about enzymes in the biota database
    It browses enyme table to collect and process statistics informations
    
    The process can provide general statistics information about the table or more 
    specific informations with about enzymes of a given organism
    """
    input_specs = {}
    output_specs = {'EnzymeStatistics': EnzymeStatistics}
    config_specs = {
        'global_informations': {"type": 'bool', "default": True}, 
        'organism': {"type": 'str', "default": ""}
    }

    def task(self): 
        params = self.config.data

        se = EnzymeStatistics()

        if (self.get_param('global_informations')): # Case if the user want only global information about the Enzyme table
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
        
            #print('Extract total number of enzyme')
            enzymes = Enzyme.select()
            size = len(enzymes)
            se.set_enzyme_count(len(enzymes))

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

                    if(enzyme.ec not in dict_enz_funyme_functions_classes.keys()):
                        dict_enz_funyme_functions_classes[enzyme.ec] =1
                    else:
                        dict_enz_funyme_functions_classes[enzyme.ec] += 1

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
                    if(enzyme.ec not in dict_enz_funyme_functions_classes.keys()):
                        dict_enz_funyme_functions_classes[enzyme.ec] =1
                    else:
                        dict_enz_funyme_functions_classes[enzyme.ec] += 1
                    
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
            se.set_number_of_ec_class(len(dict_enz_funyme_functions_classes))
            se.set_number_of_entries(dict_entries)
            se.set_number_of_references(len(dict_references))
            se.set_proportion_by_ec_group(dict_proportion_ec_group)
            se.set_proportion_of_params(proportions_params)
            se.set_enzyme_count(len(enzymes_organism))
            se.set_uniprots_referenced(uniprot_id_number) 

        self.output['EnzymeStatistics'] = se

EnzymeBTODeffered.set_model(EnzymeBTO)
