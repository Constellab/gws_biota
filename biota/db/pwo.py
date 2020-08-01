# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws.prism.controller import Controller
from gws.prism.model import Resource, DbManager
from biota._helper.ontology import Onto as OntoHelper

class PWO(Resource):
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
    name = CharField(null=True, index=True)
    _table_name = 'pwo'

    # -- C --

    @classmethod
    def create_pwo_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `pwo` database
        
        :param biodata_db_dir: path of the :file:`pwo.obo`
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        OntoHelper.correction_of_pwo_file(biodata_db_dir, files["pwo_data"], 'pwo_out_test.obo')
        ontology = OntoHelper.create_ontology_from_obo(biodata_db_dir, 'pwo_out_test.obo')
        list_of_pwo = OntoHelper.parse_pwo_terms_from_ontology(ontology)

        pwos = [cls(data = dict_) for dict_ in list_of_pwo]
        for pwo in pwos:
            pwo.set_pwo_id( pwo.data["id"] )
            pwo.set_name( pwo.data["name"] )

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
    def create_table(cls, *arg, **kwargs):
        """
        Creates `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*arg, **kwargs)
        PWOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        """
        Returns the definition of the got term

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

    def set_name(self, name__):
        """
        Sets the name of the pwo term

        :param name: The name
        :type name: str
        """
        self.name = name__    

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
                val = {'pwo': self.id, 'ancestor': PWO.get(PWO.pwo_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)

    class Meta():
        table_name = 'pwo'

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
        table_name = 'pwo_ancestors'
        database = DbManager.db
        indexes = (
            (('pwo', 'ancestor'), True),
        )

Controller.register_model_classes([PWO])