from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.prism.ontology import Ontology
from biota.helper.ontology import Onto

####################################################################################
#
# GO class
#
####################################################################################

class GO(Ontology):
    """

    This class allows to load GO entities in the database
    Through this class, the user has access to the entire GO ontology

    The Gene Ontology (GO) is a major bioinformatics initiative to unify 
    the representation of gene and gene product attributes across all species.
    
    GO entities are automatically created by the create_go() method

    :type go_id: CharField 
    :property go_id: id of the go term
    :type name: CharField 
    :property name: name of the go term
    :type namespace: CharField 
    :property namespace: namespace of the go term

    """
    go_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    namespace = CharField(null=True, index=True)
    _table_name = 'go'

    # -- C -- 
    
    @classmethod
    def create_table(cls, *arg, **kwargs):
        """

        Creates tables related to GO entities such as go, go ancestors, etc...
        Uses the super() method of the gws.model object

        """
        super().create_table(*arg, **kwargs)
        GOAncestor.create_table()

    @classmethod
    def create_go(cls, input_db_dir, **files):
        """
        This method allows biota module to create GO entities

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the go.obo file
        :type files_test: dict
        :param files_test: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """
        onto_go = Onto.create_ontology_from_obo(input_db_dir, files["go_data"])
        list_go = Onto.parse_obo_from_ontology(onto_go)
        
        gos = [cls(data = dict_) for dict_ in list_go]
        for go in gos:
            go.set_go_id(go.data["id"])
            go.set_name(go.data["name"])
            go.set_namespace(go.data["namespace"])

        cls.save_all(gos)

        vals = []
        bulk_size = 750

        with DbManager.db.atomic() as transaction:
            try:
                for go in gos:
                    if 'ancestors' in go.data.keys():
                        val = go._get_ancestors_query()
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
        
        Drops tables related to GO entities such as go, go ancestors, etc...
        Uses the super() method of the gws.model object

        """
        GOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    
    @property
    def definition(self):
        """

            return self.definition

        """
        return self.data["definition"]

    # -- S --

    def set_definition(self, def__):
        """

            set self.definition
        
        """
        self.definition = def__

    def set_go_id(self, id):
        """

            set self.go_id
        
        """
        self.go_id = id

    def set_name(self, name__):
        """

            set self.name
        
        """
        self.name = name__
    
    def set_namespace(self, namespace__):
        """

            set self.namespace
        
        """
        self.namespace = namespace__
    
    def _get_ancestors_query(self):
        """

        look for the go term ancestors and returns all go-go_ancestors relations in a list 
        :returns: a list of dictionnaries in the following format: {'go': self.id, 'ancestor': ancestor.id}
        :rtype: list
        
        """
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.go_id):
                val = {'go': self.id, 'ancestor': GO.get(GO.go_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)

    class Meta():
        table_name = 'go'

class GOAncestor(PWModel):
    """
    
    This class refers to go ancestors, wihch are go entities but also parent of go element

    GOAncestor entities are created by the create_go() method which get ancestors of the go term by
    calling __get_ancestors_query()

    :type go: GO 
    :property go: id of the concerned go term
    :type ancestor: GO 
    :property ancestor: ancestor of the concerned go term
    
    """
    go = ForeignKeyField(GO)
    ancestor = ForeignKeyField(GO)
    class Meta:
        table_name = 'go_ancestors'
        database = DbManager.db
        indexes = (
            (('go', 'ancestor'), True),
        )

class GOJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
        {
            "id": "{{view_model.model.go_id}}",
            "name": "{{view_model.model.name}}"
        }
        """)
    
class GOJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""{
            "id": "{{view_model.model.go_id}}",
            "name": "{{view_model.model.name}}",
            "namespace": "{{view_model.model.namespace}}",
            "definition": "{{view_model.model.definition}}",
            "ancestors": "{{view_model.display_ancestors()}}"}
        """)

    def display_ancestors(self):
        q = GOAncestor.select().where(GOAncestor.go == self.model.id)
        list_ancestors = []
        for i in range(0, len(q)):
            list_ancestors.append(q[i].ancestor.go_id)
        return(list_ancestors)