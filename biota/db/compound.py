# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, FloatField, TextField, IntegerField
from biota.db.entity import Entity

class Compound(Entity):
    """
    This class represents metabolic compounds from the ChEBI database.
    
    Chemical Entities of Biological Interest (ChEBI) includes an
    ontological classification, whereby the relationships between molecular 
    entities or classes of entities and their parents and/or children are 
    specified (https://www.ebi.ac.uk/chebi/). ChEBI data are available under the Creative Commons License (CC BY 4.0),
    https://creativecommons.org/licenses/by/4.0/

    :property name : name of the compound
    :type name : CharField
    :property chebi_id: chebi accession number
    :type chebi_id: CharField
    :property formula: chimical formula
    :type formula: CharField
    :property mass: mass of the compound
    :type mass: FloatField 
    :property charge: charge of the compound
    :type charge: FloatField
    """
    
    name = CharField(null=True, index=True)
    inchi = CharField(null=True, index=True)
    inchi_key = CharField(null=True, index=True)
    smiles = CharField(null=True, index=True)
    uipac = CharField(null=True, index=True)
    chebi_id = CharField(null=True, index=True)
    chebi_star = IntegerField(null=True, index=True)
    metacyc_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    average_mass = FloatField(null=True, index=True)
    monoisotopic_mass = FloatField(null=True, index=True)
    charge = IntegerField(null=True, index=True)

    _table_name = 'compound'

    atom_block = {
        0:'x', 
        1:'y', 
        2:'z', 
        3:'atom_symbol', 
        4:'mass_difference', 
        5:'charge', 
        6:'atom_stereo_parity', 
        7:'hydrogen_count',
        8:'stereo_care_box', 
        9:'valence',
        10:'atom_atom_mapping_number',
        11:'inversion_retention_flag',
        12:'exact_change_flag'
    }

    bond_block = {
        0:'first_atom_number',
        1:'second_atom_number',
        2:'bond_type',
        3:'bond_stereo',
        4:'bond_topology',
        5:'reacting_center_status'
    }

    # -- C -- 

    @classmethod
    def create_compound_db(cls, biodata_dir = None, **kwargs):
        from biota._helper.chebi import Chebi as ChebiHelper
        ctf = ChebiHelper.read_sdf(biodata_dir, kwargs['chebi_sdf_file'])
        job = kwargs.get('job',None)

        n = len(ctf.sdfdata)
        
        str_mapping = {
            'name': 'ChEBI Name',
            'inchi': 'InChI',
            'inchi_key': 'InChIKey',
            'smiles': 'SMILES',
            'chebi_id': 'ChEBI ID',
            'uipac': 'IUPAC Names',
            'formula': 'Formulae',
            'metacyc_id': 'MetaCyc Database Links',
            'kegg_id': 'KEGG COMPOUND Database Links',
        }
        
        comps = []
        for i in range(0,n):
            comp = Compound()

            if not job is None:
                comp._set_job(job)

            for k in str_mapping:
                val = ctf.sdfdata[i].get(str_mapping[k],'')
                if isinstance(val, list):
                    setattr(comp, k, val[0])
                else:
                    setattr(comp, k, val)

            comp.chebi_star = int(ctf.sdfdata[i]['Star'][0])
            comp.average_mass = float(ctf.sdfdata[i]['Mass'][0])
            comp.monoisotopic_mass = float(ctf.sdfdata[i]['Monoisotopic Mass'][0])
            comp.charge = int(ctf.sdfdata[i]['Charge'][0])

            comp.data = {
                'definition': ctf.sdfdata[i].get('Definition',[''])[0],
                'wikipedia': ctf.molfiles[i].get('Wikipedia Database Links',[''])[0],
                'lipidmaps_id': ctf.sdfdata[i].get('LIPID MAPS instance Database Links',[''])[0],
                'hmdb_id': ctf.sdfdata[i].get('HMDB Database Links',[''])[0],
                'synonyms': ctf.sdfdata[i].get('Synonyms',[]),
                'pubmed': ctf.sdfdata[i].get('PubMed citation Links',[]),
                'structure': cls.__extract_structure(ctf.molfiles[i]),
                'last_modified': ctf.sdfdata[i].get('Last Modified',[''])[0]
            }
            comps.append(comp)

            if len(comps) >= 500:
                cls.save_all(comps)
                comps = []
        
        if len(comps) > 0:
            cls.save_all(comps)

    @property
    def structure(self):
        struct = {'atoms': [], 'bonds': []}
        structure_data = self.data['structure']

        for matrix_atom in structure_data['atoms']:
            atom = {}
            for idx in self.atom_block:
                name = self.atom_block[idx]
                atom[name] = matrix_atom[idx]

            struct['atoms'].append(atom)

        for matrix_bond in structure_data['bonds']:
            bond = {}
            for idx in self.bond_block:
                name = self.bond_block[idx]
                bond[name] = matrix_bond[idx]

            struct['bonds'].append(bond)

        return struct

    @classmethod
    def __extract_structure(cls, mols):
        data = {'atoms': [], 'bonds': []}
        for atom in mols.atoms:
            tab = []
            for k in cls.atom_block.values():
                tab.append(atom[k])

            data['atoms'].append(tab)

        for bond in mols.bonds:
            tab = []
            for k in cls.bond_block.values():
                tab.append(bond[k])

            data['bonds'].append(tab)


        return data

    # -- S --

    def set_name(self, name):
        self.name = name
    
    def set_chebi_id(self, chebi_id):
        self.chebi_id = chebi_id
    
    def set_formula(self, formula):
        self.formula = formula
    
    def set_average_mass(self, mass):
        self.average_mass = mass
    
    def set_monoisotopic_mass(self, mass):
        self.monoisotopic_mass = mass
    
    def set_charge(self, charge):
        self.charge = charge