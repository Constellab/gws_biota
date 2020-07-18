from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.ontology import Ontology
from onto.ontology import Onto

####################################################################################
#
# GO class
#
####################################################################################

class GO(Ontology):
    go_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    namespace = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'go'

    # setters
    def set_definition(self, def__):
        self.definition = def__

    def set_go_id(self, id):
        self.go_id = id

    def set_name(self, name__):
        self.name = name__
    
    def set_namespace(self, namespace__):
        self.namespace = namespace__
    
    def __get_ancestors_query(self):
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.go_id):
                val = {'go': self.id, 'ancestor': GO.get(GO.go_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)
    
    # inserts
    @classmethod
    def insert_definition(cls, list__, key):
        for go in list__:
            go.set_definition(go.data[key])

    @classmethod
    def insert_go_id(cls, list__, key):
        for go in list__:
            go.set_go_id(go.data[key])

    @classmethod
    def insert_name(cls, list__, key):
        for go in list__:
            go.set_name(go.data[key])

    @classmethod
    def insert_namespace(cls, list__, key):
        for go in list__:
            go.set_namespace(go.data[key])

    #  reate and drop table methods
    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        GOAncestor.create_table()

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        GOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # create go
    @classmethod
    def create_go(cls, input_db_dir, **files_test):
        onto_go = Onto.create_ontology_from_obo(input_db_dir, files_test["go_data"])
        list_go = Onto.parse_obo_from_ontology(onto_go)
        gos = [cls(data = dict_) for dict_ in list_go]
        cls.insert_go_id(gos,"id")
        cls.insert_name(gos, "name")
        cls.insert_namespace(gos, "namespace")
        cls.insert_definition(gos, "definition")
        cls.save_all(gos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for go in gos:
                    if 'ancestors' in go.data.keys():
                        val = go.__get_ancestors_query()
                        if len(val) != 0:
                            for v in val:
                                vals.append(v)
                                if len(vals) == bulk_size:
                                    print("---------")
                                    print(len(vals))
                                    GOAncestor.insert_many(vals).execute()
                                    vals = []
                            
                            if len(vals) != 0:
                                GOAncestor.insert_many(vals).execute()
                                vals = []

            except:
                transaction.rollback()

    class Meta():
        table_name = 'go'

class GOAncestor(PWModel):
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
            "id": {{view_model.model.go_id}},
            "name": {{view_model.model.name}}
            }
        """)
    
class GOJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.go_id}},
            "name": {{view_model.model.name}},
            "namespace": {{view_model.model.namespace}},
            "definition": {{view_model.model.definition}},
            "ancestors": {{view_model.display_ancestors()}}
            }
        """)

    def display_ancestors(self):
        q = GOAncestor.select().where(GOAncestor.go == self.model.id)
        list_ancestors = []
        for i in range(0, len(q)):
            list_ancestors.append(q[i].ancestor.go_id)
        return(list_ancestors)