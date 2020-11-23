# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from biota.db.ontology import Ontology
from biota.db.base import Base, DbManager

class BTO(Ontology):
    """
    This class represents BTO terms.
    
    The BTO (BRENDA Tissue Ontology) is a comprehensive structured 
    encyclopedia. It providies terms, classifications, and definitions of tissues, organs, anatomical structures, 
    plant parts, cell cultures, cell types, and cell lines of organisms from all taxonomic groups 
    (animals, plants, fungis, protozoon) as enzyme sources (https://www.brenda-enzymes.org/). 
    BRENDA data are available under the Creative Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    :property bto_id: id of the bto term
    :type bto_id: class:`peewee.CharField`
    :property name: name of the bto term
    :type name: class:`peewee.CharField` 
    """
    bto_id = CharField(null=True, index=True)
    _table_name = 'bto'

    # -- A --

    @property
    def ancestors(self):
        bto_ids = self.data['ancestors']
        if self.bto_id in bto_ids:
            bto_ids.remove(self.bto_id)

        return BTO.select().where(BTO.bto_id.in_(bto_ids))

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `bto` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        BTOAncestor.create_table()
        
    @classmethod
    def create_bto_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `bto` database

        :param biodata_dir: path of the :file:`bto.json`
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data file names
        :type kwargs: dict
        """

        from biota._helper.ontology import Onto as OntoHelper

        list_bto = OntoHelper.parse_bto_from_json(biodata_dir, kwargs['bto_file'])
        btos = [cls(data = dict_) for dict_ in list_bto]
        job = kwargs.get('job',None)

        for bto in btos:
            bto.set_bto_id( bto.data["id"] )
            bto.set_name( bto.data["title"] )

            del bto.data["id"]
            
            if not job is None:
                bto._set_job(job)

        cls.save_all(btos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for bt in btos:
                    val = bt.__build_insert_query_vals_of_ancestors()
                    if len(val) != 0:
                        for v in val:
                            vals.append(v)
                            if len(vals) == bulk_size:
                                BTOAncestor.insert_many(vals).execute()
                                vals = []
                        
                        if len(vals) != 0:
                            BTOAncestor.insert_many(vals).execute()
                            vals = []

            except:
                transaction.rollback()

    # -- D --

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        BTOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- G --

    def __build_insert_query_vals_of_ancestors(self):
        """
        Look for the bto term ancestors and returns all bto-bto_ancetors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'bto': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        for i in range(0,len(self.data['ancestors'])):
            if (self.data['ancestors'][i] != self.bto_id):
                val = {'bto': self.id, 'ancestor': BTO.get(BTO.bto_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return vals
        
    # -- R --
    # def remove_ancestor(self, ancestor):
    #     """
    #     Remove a bto ancestor.
    #     """
    #     Q = BTOAncestor.delete().where(BTOAncestor.bto == self.id, BTOAncestor.ancestor == ancestor.id)
    #     Q.execute()

    # -- S --

    def set_bto_id(self, bto_id):
        """
        Set the bto_id accessor

        :param: bto_id: The bto_id accessor
        :type bto_id: str
        """
        self.bto_id = bto_id

class BTOAncestor(PWModel):
    """
    This class defines the many-to-many relationship between the bto terms and their ancestors

    :property bto: id of the concerned bto term
    :type bto: CharField 
    :property ancestor: ancestor of the concerned bto term
    :type ancestor: CharField 
    """
    bto = ForeignKeyField(BTO)
    ancestor = ForeignKeyField(BTO)
    
    class Meta:
        table_name = 'bto_ancestors'
        database = DbManager.db
        indexes = (
            (('bto', 'ancestor'), True),
        )
