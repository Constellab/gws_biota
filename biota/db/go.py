# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from biota.db.base import Base, DbManager
from biota.db.ontology import Ontology

class GO(Ontology):
    """
    This class represents GO terms.

    The Gene Ontology (GO) is a major bioinformatics initiative to unify
    the representation of gene and gene product attributes across all 
    species (http://geneontology.org/). GO data are available under the Creative 
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
    
    :property go_id: id of the go term
    :type go_id: CharField 
    :property name: name of the go term
    :type name: CharField 
    :property namespace: namespace of the go term
    :type namespace: CharField 
    """
    go_id = CharField(null=True, index=True)
    namespace = CharField(null=True, index=True)
    
    _fts_fields = { **Ontology._fts_fields, 'definition': 1.0 }
    _table_name = 'biota_go'

    # -- C -- 
    
    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `go` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        GOAncestor.create_table()

    @classmethod
    def create_go_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `go` database

        :param biodata_dir: path of the :file:`go.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.ontology import Onto as OntoHelper

        job = kwargs.get('job',None)
        onto_go = OntoHelper.create_ontology_from_obo(biodata_dir, kwargs['go_file'])
        list_go = OntoHelper.parse_obo_from_ontology(onto_go)
        
        gos = [cls(data = dict_) for dict_ in list_go]
        for go in gos:
            go.set_go_id(go.data["id"])
            go.set_name(go.data["title"])
            go.set_namespace(go.data["namespace"])

            del go.data["id"]

            if not job is None:
                go._set_job(job)

        cls.save_all(gos)

        vals = []
        bulk_size = 750

        with DbManager.db.atomic() as transaction:
            try:
                for go in gos:
                    if 'ancestors' in go.data.keys():
                        val = go.__build_insert_query_vals_of_ancestors()
                        if len(val) != 0:
                            for v in val:
                                vals.append(v)
                                if len(vals) == bulk_size:
                                    GOAncestor.insert_many(vals).execute()
                                    vals = []
                            
                            if len(vals) != 0:
                                GOAncestor.insert_many(vals).execute()
                                vals = []

            except:
                transaction.rollback()

  
    # -- D --

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `go` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        GOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    
    @property
    def definition(self):
        """
        Returns the definition of the got term

        :returns: The definition
        :rtype: str
        """
        return self.data["definition"]

    # -- S --

    def set_definition(self, definition):
        """
        Set the definition of the go term

        :param definition: The definition
        :type definition: str
        """
        self.definition = definition

    def set_go_id(self, id):
        """
        Sets the id of the go term

        :param id: The id
        :type id: str
        """
        self.go_id = id
    
    def set_namespace(self, namespace):
        """
        Sets the namespace of the go term

        :param namespace: The namespace
        :type namespace: str
        """
        self.namespace = namespace
    
    def __build_insert_query_vals_of_ancestors(self):
        """
        Look for the go term ancestors and returns all go-go_ancestors relations in a list 

        :returns: A list of dictionnaries in the following format: {'go': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.go_id):
                val = {'go': self.id, 'ancestor': GO.get(GO.go_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)


class GOAncestor(PWModel):
    """
    This class defines the many-to-many relationship between the go terms and theirs ancestors

    :property go: id of the go term
    :type go: GO 
    :property ancestor: ancestor of the go term
    :type ancestor: GO 
    """

    go = ForeignKeyField(GO)
    ancestor = ForeignKeyField(GO)
    
    class Meta:
        table_name = 'biota_go_ancestors'
        database = DbManager.db
        indexes = (
            (('go', 'ancestor'), True),
        )
