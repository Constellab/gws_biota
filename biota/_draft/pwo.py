# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws.controller import Controller
from gws.model import Resource

from biota.ontology import Ontology
from biota.base import Base, DbManager

class PWO(Ontology):
    """
    This class represents Pathway Ontology (PWO) terms

    The Pathway Ontology is a controlled vocabulary for pathways that provides 
    standard terms for the annotation of gene products to pathways. It is under 
    development at Rat Genome Database (https://rgd.mcw.edu).
    Pathway Ontology is under the Creative Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
    
    :property pwo_id: id of the pwo term
    :type pwo_id: class:`peewee.CharField` 
    :property name: name of the pwo term
    :type name: class:`peewee.CharField` 
    """

    pwo_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    brenda_id = CharField(null=True, index=True)
    metacyc_id = CharField(null=True, index=True)

    _fts_fields = { **Ontology._fts_fields, 'definition': 1.0 }
    _table_name = 'biota_pwo'

    # -- C --

    @classmethod
    def create_pwo_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `pwo` database
        
        :param biodata_dir: path of the :file:`pwo.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.ontology import Onto as OntoHelper

        job = kwargs.get('job',None)
        data_dir, corrected_file_name = OntoHelper.correction_of_pwo_file(biodata_dir, kwargs['pwo_file'])
        ontology = OntoHelper.create_ontology_from_obo(data_dir, corrected_file_name)
        list_of_pwo = OntoHelper.parse_pwo_terms_from_ontology(ontology)

        pwos = [cls(data = dict_) for dict_ in list_of_pwo]
        for pwo in pwos:
            pwo.set_pwo_id( pwo.data["id"] )
            pwo.set_name( pwo.data["title"] )
            if not job is None:
                pwo._set_job(job)

            del pwo.data["id"]

        cls.save_all(pwos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for pwo in pwos:
                    if 'ancestors' in pwo.data.keys():
                        val = pwo.__build_insert_query_vals_of_ancestors()
                        if len(val) != 0:
                            for v in val:
                                vals.append(v)
                                if len(vals) == bulk_size:
                                    PWOAncestor.insert_many(vals).execute()
                                    vals = []
                            
                            if len(vals) != 0:
                                PWOAncestor.insert_many(vals).execute()
                                vals = []
            except:
                transaction.rollback()

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        PWOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        """
        Returns the definition of the go term

        :returns: The definition
        :rtype: str
        """
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        PWOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S -- 

    def set_pwo_id(self, pwo_id):
        """
        Sets the pwo id of the pwo term

        :param pwo_id: The pwo id
        :type pwo_id: str
        """
        self.pwo_id = pwo_id
    
    def __build_insert_query_vals_of_ancestors(self):
        """
        Look for the pwo term ancestors and returns all pwo-pwo_ancestors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'pwo': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.pwo_id):
                val = {
                    'pwo': self.id, 
                    'ancestor': PWO.get(PWO.pwo_id == self.data['ancestors'][i]).id 
                }
                vals.append(val)
        return(vals)


class PWOAncestor(PWModel):
    """
    This class defines the many-to-many relationship between the pwo terms and theirs ancestors

    :type pwo: CharField 
    :property pwo: id of the concerned pwo term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned pwo term
    """

    pwo = ForeignKeyField(PWO)
    ancestor = ForeignKeyField(PWO)
    
    class Meta:
        table_name = 'biota_pwo_ancestors'
        database = DbManager.db
        indexes = (
            (('pwo', 'ancestor'), True),
        )
