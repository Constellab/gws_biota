# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from peewee import ForeignKeyField, CharField

from gws.prism.controller import Controller
from gws.prism.model import DbManager

from biota._helper.brenda import Brenda
from biota.db.entity import Entity
from biota.db.protein import Protein

class Enzyme(Entity):
    """
    This class represents enzymes.
    """
    
    ec = CharField(null=True, index=True)
    protein = ForeignKeyField(Protein, backref = 'enzyme', null = True)
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

        :param biodata_db_dir: path of the :file:`go.obo`
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """
        brenda = Brenda(os.path.join(biodata_db_dir, files['brenda_file']))
        list_enzymes = brenda.parse_all_protein_to_dict()
        proteins = {}
        enzymes = {}
        for d in list_enzymes:
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

    # -- D -- 
    
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_tables`
        """
        super().drop_table(*arg, **kwargs)

    class Meta():
        table_name = 'enzyme'


Controller.register_model_classes([Enzyme])