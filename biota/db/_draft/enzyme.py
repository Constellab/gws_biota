# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import ForeignKeyField, CharField

from gws.controller import Controller

from biota.db.entity import Entity
from biota.db.enzyme import Enzyme
from biota.db.pwo import PWO

class Enzyme(Entity):
    """
    This class represents enzymes.
    """
    
    ec = CharField(null=True, index=True)
    protein = ForeignKeyField(Enzyme, backref = 'enzyme', null = True)
    pwo = ForeignKeyField(PWO, backref = 'enzymes', null = True)

    _table_name = 'enzyme'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def go_id(self):
        return self.enzyme.uniprot_id

    @property
    def name(self):
        return self.enzyme.name

    # -- C -- 
    
    @classmethod
    def create_table(cls, *arg, **kwargs):
        """
        Creates `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*arg, **kwargs)
        Enzyme.create_table()

    @classmethod
    def create_enzyme_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `protein` database

        :param biodata_dir: path of the brenda dump file
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """

        job = kwargs.get('job',None)

        if not kwargs.get('proteins', None) is None:
            enzymes =  cls.__create_enzyme_and_protein_dbs(kwargs['proteins'], job=job)
        else:
            from biota._helper.bkms import BKMS
            from biota._helper.brenda import Brenda
            brenda = Brenda(os.path.join(biodata_dir, kwargs['brenda_file']))
            proteins = brenda.parse_all_enzyme_to_dict()
            enzymes = cls.__create_enzyme_and_protein_dbs(proteins, job=job)

        if (not biodata_dir is None) and (not kwargs.get('bkms_file', None) is None):
            from biota._helper.bkms import BKMS
            list_of_bkms = BKMS.parse_csv_from_file(biodata_dir, kwargs['bkms_file'])
            cls.__update_pathway_from_bkms(list_of_bkms)

        return enzymes

    @classmethod
    def __create_enzyme_and_protein_dbs(cls, list_of_proteins, job=None):
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

            protein = Enzyme(
                name = d['RN'], 
                uniprot_id = d['uniprot'], 
                data = data
            )
            
            enzyme = Enzyme(
                ec = ec, 
                protein = protein
            )     
            
            if not job is None:
                protein._set_job(job)
                enzyme._set_job(job)

            proteins[ec] = protein
            enzymes[ec] = enzyme

        Enzyme.save_all(proteins.values()) 
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

    # -- E --

    @property
    def enzyme(self):
        from biota.db.enzyme import Enzyme
        return Enzyme.select().where(Enzyme.enzyme == self)

    # -- U --

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the enzyme tissue locations and if so, 
        connects the enzyme and tissues by adding an enzyme-tissues relation 
        in the enzyme_btostable
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