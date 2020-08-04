# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import ForeignKeyField, CharField

from gws.prism.controller import Controller
from gws.prism.model import DbManager

from biota.db.entity import Entity
from biota.db.protein import Protein
from biota.db.pwo import PWO

class Enzyme(Entity):
    """
    This class represents enzymes.
    """
    
    ec = CharField(null=True, index=True)
    protein = ForeignKeyField(Protein, backref = 'enzyme', null = True)
    pwo = ForeignKeyField(PWO, backref = 'enzymes', null = True)

    _table_name = 'enzyme'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def go_id(self):
        return self.protein.uniprot_id

    @property
    def name(self):
        return self.protein.name

    @property
    def uniprot_id(self):
        return self.protein.uniprot_id

    # -- C -- 
    
    @classmethod
    def create_table(cls, *arg, **kwargs):
        """
        Creates `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*arg, **kwargs)
        Protein.create_table()

    @classmethod
    def create_enzyme_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `protein` database

        :param biodata_db_dir: path of the brenda dump file
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.bkms import BKMS
        from biota._helper.brenda import Brenda

        brenda = Brenda(os.path.join(biodata_db_dir, files['brenda_file']))

        list_of_proteins = brenda.parse_all_protein_to_dict()
        cls.__create_enzyme_and_protein_dbs(list_of_proteins)

        list_of_bkms = BKMS.parse_csv_from_file(biodata_db_dir, files['bkms_file'])
        cls.__update_pathway_from_bkms(list_of_bkms)

    @classmethod
    def __create_enzyme_and_protein_dbs(cls, list_of_proteins):
        proteins = {}
        enzymes = {}
        info = ['SN','SY']
        for d in list_of_proteins:
            ec = d['ec']

            if ec in enzymes:
                continue
            
            data = {'source': 'brenda'}  
            for k in info:
                if k in d:
                    data[k] = d[k]

            protein = Protein(
                name = d['RN'], 
                uniprot_id = d['uniprot'], 
                data = data
            )
            
            enzyme = Enzyme(
                ec = ec, 
                protein = protein
            )     

            proteins[ec] = protein
            enzymes[ec] = enzyme

        Protein.save_all(proteins.values()) 
        Enzyme.save_all(enzymes.values())

        return enzymes

    # -- D -- 
    
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_tables`
        """
        super().drop_table(*arg, **kwargs)

    # -- U --

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the enzyme_function tissue locations and if so, 
        connects the enzyme_function and tissues by adding an enzyme_function-tissues relation 
        in the enzyme_function_btostable
        """

        enzymes = {}
        bulk_size = 750
        dbs = ['brenda', 'kegg', 'metacyc']
        for bkms in list_of_bkms:
            ec = bkms["ec_number"]

            Q = Enzyme.select().where(Enzyme.ec == ec)
            for enzyme in Q:
                for k in dbs:

                    if bkms.get(k+'_pathway_name',"") != "":
                        pwy_id = bkms.get(k+'_pathway_id', "ID")
                        pwy_name = bkms[k+'_pathway_name']
                        enzyme.data[k+'_pathway'] = { pwy_id : pwy_name }

                enzymes[enzyme.ec] = enzyme

                if len(enzymes.keys()) >= bulk_size:
                    Enzyme.save_all(enzymes.values())
                    enzymes = []

        if len(enzymes) > 0:
            Enzyme.save_all(enzymes.values())

    class Meta():
        table_name = 'enzyme'


Controller.register_model_classes([Enzyme])