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
from biota.db.bto import BTO as BiotaBTO
from biota.db.protein import Protein


EnzymeBTODeffered = DeferredThroughModel()

class Param():
    """
    Adpater class that represents a BRENDA parameter

    :property what: Description of the parameter
    :type what: str
    :property value: Value of the parameter
    :type value: str
    :property refs: References numbers associated with the parameter value
    :type refs: list
    :property full_refs: Full references (pubmed id, or description) associated with the parameter value
    :type full_refs: list
    :property comments: Short comments extracted from the references 
    :type comments: str
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
        Returns True if the parameter exists (i.e. `value` is not `None`) 
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

    _whats = dict(
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
                        what = self._whats[self._name]
                    )
                elif isinstance(self._data[index], dict):
                    return Param(
                        data = self._data[index],
                        refs = self._data[index].get("refs", None),
                        full_refs = self._full_refs,
                        comments = self._data[index].get("comment", None),
                        what = self._whats[self._name]
                    )
                else:
                    return Param()    
            else:
                return Param()
        else:
            return Param()

    def __str__(self):
        """
        String representation. 
        """
        
        from pprint import pformat
        return pformat({
            "name" : self._name,
            "data" : self._data,
            "full_refs" : self._full_refs
        })

class EnzymePathway(Base):
    """
    This class represents enzyme pathway.
    """

    ec_number = CharField(null=True, index=True)
    _table_name = 'biota_enzyme_pathway'

class Enzo(Base):
    """
    This class represents enzyme ortholog.
    """

    ec_number = CharField(null=True, index=True, unique=True)
    pathway = ForeignKeyField(EnzymePathway, backref = 'enzos', null = True)
    _table_name = 'biota_enzo'

    # -- E --

    @property   
    def enzymes( self, tax_id: str = None, tax_name: str = None ):
        Q = Enzyme.select().where(Enzyme.ec_number == self.ec_number)
        if not tax_id is None:
            Q = Q.where(Enzyme.tax_id == tax_id)
 
        return Q.order_by(Enzyme.data['RN'].desc())

    # -- G --

    def get_title(self, default=""):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme ortholog
        :rtype: str
        """
        
        return self.data.get("RN", [default])[0].capitalize()

    # -- N --

    @property
    def synomyms(self):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme orthologue
        :rtype: str
        """
        
        return ",".join([ sn.capitalize() for sn in self.data.get("SN", ['']) ])

class Enzyme(Base):
    """
    This class represents enzymes extracted from open databases.

    :property go_id: GO term id
    :type go_id: str
    :property name: name of the compound
    :type name: str
    :property ec: ec accession number
    :type ec: str
    :property taxonomy: taxonomy id that gives the organism
    :type taxonomy: str
    :property bto: bto id that gives the tissue location 
    :type bto: class:biota.db.BTO
    :property uniprot_id: uniprot id of the enzyme
    :type uniprot_id: str
    
    * Uniprot:
        The Universal Protein Resource (UniProt) is a comprehensive resource for protein sequence and annotation data. 
        The UniProt databases are the UniProt Knowledgebase (UniProtKB), the UniProt Reference Clusters (UniRef), 
        and the UniProt Archive (UniParc). The UniProt consortium and host institutions EMBL-EBI, SIB and PIR are 
        committed to the long-term preservation of the UniProt databases.
    * Brenda:
        BRENDA is the main collection of enzyme functional data available to the scientific community 
        (https://www.brenda-enzymes.org/). BRENDA data are available under the Creative 
        Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
    * BKMS:
        BKMS-react is an integrated and non-redundant biochemical reaction database 
        containing known enzyme-catalyzed and spontaneous reactions. 
        Biochemical reactions collected from BRENDA, KEGG, MetaCyc and 
        SABIO-RK were matched and integrated by aligning substrates and products.
    """
    
    #pathway = ForeignKeyField(EnzymePathway, backref = 'enzymes', null = True)
    ec_number = CharField(null=True, index=True)
    uniprot_id = CharField(null=True, index=True)
    
    tax_superkingdom = CharField(null=True, index=True)
    tax_clade = CharField(null=True, index=True)
    tax_kingdom = CharField(null=True, index=True)
    tax_subkingdom = CharField(null=True, index=True)
    tax_class = CharField(null=True, index=True)    
    tax_phylum = CharField(null=True, index=True)
    tax_subphylum = CharField(null=True, index=True)
    tax_order = CharField(null=True, index=True)
    tax_genus = CharField(null=True, index=True)
    tax_family = CharField(null=True, index=True)
    tax_species = CharField(null=True, index=True)
    
    tax_id = CharField(null=True, index=True)
    
    bto = ManyToManyField(BiotaBTO, through_model = EnzymeBTODeffered)
    
    _fts_fields = { **Base._fts_fields, 'ec': 2.0, 'uniprot': 2.0, 'RN': 2.0, "SN": 2.0, "SY": 2.0, 'organism': 1.0 }
    _table_name = 'biota_enzymes'
    
    # -- A --
    
    def as_json(self, jsonifiable_data_keys: list=['title', 'description'], **kwargs):
        
        return super().as_json(
            jsonifiable_data_keys=jsonifiable_data_keys, 
            **kwargs
        )
    
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

        # save EnzymePathway
        pathways = {}
        for d in list_of_enzymes:
            ec = d['ec']
            if not ec in pathways:
                pathways[ec] = EnzymePathway(ec_number = ec)

                if not job is None:
                    pathways[ec]._set_job(job)
                
        EnzymePathway.save_all(pathways.values())

        # save Enzo
        enzos = {}
        for d in list_of_enzymes:
            ec = d['ec']
            if not ec in enzos:
                enzos[ec] = Enzo(
                    ec_number = ec,
                    data = {
                        'RN': d['RN'],
                        'SN': d.get('SN', []),
                        'SY': d.get('SY', [])
                    }
                )
                 
                enzos[ec].set_name(d['RN'][0])
                
                if not job is None:
                    enzos[ec]._set_job(job)
                    enzos[ec].pathway = pathways[ec]
        Enzo.save_all(enzos.values())
        
        # save Enzymes
        enzymes = []
        for d in list_of_enzymes:
            ec = d['ec']
            enz = Enzyme(
                ec_number = ec,
                uniprot_id = d["uniprot"],
                data = d
            )

            enz.set_name(d['RN'][0])

            if not job is None:
                enz._set_job(job)
                #enz.pathway = pathways[ec]
    
            #del d["RN"]
            #del d["ec"]
            #del d["uniprot"]

            enzymes.append(enz)

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
        
        EnzymePathway.create_table()
        Enzo.create_table()
        super().create_table(*args, **kwargs)
        EnzymeBTO.create_table()

    # -- D -- 

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        
        Enzo.drop_table()
        EnzymePathway.drop_table(*args, **kwargs)
        EnzymeBTO.drop_table(*args, **kwargs)
        super().drop_table(*args, **kwargs)
    
    # -- F --
    
    @property
    def protein(self):
        try:
            return Protein.get(Protein.uniprot_id == self.uniprot_id)
        except:
            return None

    # -- G --

    def get_title(self, default=""):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme ortholog
        :rtype: str
        """
        
        return self.data.get("RN", [default])[0].capitalize()

    # -- N --

    @property
    def synomyms(self):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme orthologue
        :rtype: str
        """
        
        return ",".join([ sn.capitalize() for sn in self.data.get("SN", ['']) ])

    # -- O --

    @property
    def organism(self):
        """
        Name of the organism

        :returns: The name of the organism associated to the enzyme function
        :rtype: str
        """
        return self.data["organism"].capitalize()

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
                self.tax_id = str(self.data['taxonomy'])
                
                tax = BiotaTaxo.get(BiotaTaxo.tax_id == self.tax_id)
                setattr(self, "tax_"+tax.rank, tax.tax_id)
                
                for t in tax.ancestors:  
                    if t.rank in BiotaTaxo._tax_tree:
                        setattr(self, "tax_"+t.rank, t.tax_id)
                            
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

        pathways = {}
        bulk_size = 750
        dbs = ['brenda', 'kegg', 'metacyc']
        for bkms in list_of_bkms:
            ec_number = bkms["ec_number"]
            Q = EnzymePathway.select().where(EnzymePathway.ec_number == ec_number)
            for pathway in Q:
                for k in dbs:

                    if bkms.get(k+'_pathway_name',"") != "":
                        pwy_id = bkms.get(k+'_pathway_id', "ID")
                        pwy_name = bkms[k+'_pathway_name']
                        pathway.data[k+'_pathway'] = { pwy_id : pwy_name }

                pathways[pathway.ec_number] = pathway

                if len(pathways.keys()) >= bulk_size:
                    EnzymePathway.save_all(pathways.values())
                    pathways = {}

        if len(pathways) > 0:
            EnzymePathway.save_all(pathways.values())


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
        table_name = 'biota_enzyme_btos'
        database = DbManager.db

# Resolve dependencies.
EnzymeBTODeffered.set_model(EnzymeBTO)