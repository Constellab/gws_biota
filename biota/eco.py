# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws.controller import Controller
from biota.base import Base, DbManager
from biota.ontology import Ontology

class ECO(Ontology):
    """
    This class represents Evidence ECO terms.

    The Evidence and Conclusion Ontology (ECO) contains terms that describe 
    types of evidence and assertion methods. ECO terms are used in the process of 
    biocuration to capture the evidence that supports biological assertions 
    (http://www.evidenceontology.org/). ECO is under the Creative Commons License CC0 1.0 Universal (CC0 1.0), 
    https://creativecommons.org/publicdomain/zero/1.0/.

    :property eco_id: id of the eco term
    :type eco_id: class:`peewee.CharField`
    :property name: name of the eco term
    :type name: class:`peewee.CharField` 
    """

    eco_id = CharField(null=True, index=True)
    _ancestors = None

    _table_name = 'biota_eco'
    
    # -- A --

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors

        self._ancestors = []
        Q = ECOAncestor.select().where(ECOAncestor.eco == self.id)
        for q in Q:
            self._ancestors.append(q.ancestor)
        
        return self._ancestors

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `eco` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        ECOAncestor.create_table()

    @classmethod
    def create_eco_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `eco` database
        
        :param biodata_dir: path of the :file:`eco.obo`
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.ontology import Onto as OntoHelper

        onto_eco = OntoHelper.create_ontology_from_obo(biodata_dir, kwargs['eco_file'])
        list_eco = OntoHelper.parse_eco_terms_from_ontoloy(onto_eco)
        ecos = [cls(data = dict_) for dict_ in list_eco]
        job = kwargs.get('job',None)

        for eco in ecos:
            eco.set_eco_id( eco.data["id"] )
            eco.set_name( eco.data["title"] )

            del eco.data["id"]
            
            if not job is None:
                eco._set_job(job)

        cls.save_all(ecos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for eco in ecos:
                    if 'ancestors' in eco.data.keys():
                        val = eco._get_ancestors_query()
                        if len(val):
                            for v in val:
                                vals.append(v)
                                if len(vals) == bulk_size:
                                    ECOAncestor.insert_many(vals).execute()
                                    vals = []
                            
                            if len(vals) != 0:
                                ECOAncestor.insert_many(vals).execute()
                                vals = []
            except:
                transaction.rollback()

    # -- D --

    
    @property
    def definition(self):
        """
        return self.definition
        """
        definition = self.data["definition"]
        return ". ".join(i.capitalize() for i in definition.split(". "))

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `eco` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        ECOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    

    # -- G --

    def _get_ancestors_query(self):
        """
        Look for the eco term ancestors and returns all eco-eco_ancetors relations in a list 

        :returns: a list of dictionnaries inf the following format: {'eco': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.eco_id):
                val = {'eco': self.id, 'ancestor': ECO.get(ECO.eco_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)

    # -- S --

    def set_eco_id(self, id):
        """
        set self.eco_id
        """
        self.eco_id = id

class ECOAncestor(PWModel):
    """
    This class defines the many-to-many relationship between the eco terms and theirs ancestors

    :type eco: CharField 
    :property eco: id of the concerned eco term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned eco term
    """
    
    eco = ForeignKeyField(ECO)
    ancestor = ForeignKeyField(ECO)
    
    class Meta:
        table_name = 'biota_eco_ancestors'
        database = DbManager.db
        indexes = (
            (('eco', 'ancestor'), True),
        )
