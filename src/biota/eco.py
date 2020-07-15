from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import Model, ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.ontology import Ontology
from onto.ontology import Onto

####################################################################################
#
# ECO class
#
####################################################################################

class ECO(Ontology):
    eco_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'eco'

    # setters
    def set_definition(self, def__):
        self.definition = def__

    def set_eco_id(self, id):
        self.eco_id = id

    def set_name(self, name__):
        self.name = name__
    
    def __get_ancestors_query(self):
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.eco_id):
                val = {'eco': self.id, 'ancestor': ECO.get(ECO.eco_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)
    
    # inserts
    @classmethod
    def insert_definition(cls, list__, key):
        for eco in list__:
            eco.set_definition(eco.data[key])

    @classmethod
    def insert_eco_id(cls, list__, key):
        for eco in list__:
            eco.set_eco_id(eco.data[key])

    @classmethod
    def insert_name(cls, list__, key):
        for eco in list__:
            eco.set_name(eco.data[key])
    
    # create and drop table methods
    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        ECOAncestor.create_table()

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        ECOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    
    # create eco
    @classmethod
    def create_eco(cls, input_db_dir, **files_test):
        onto_eco = Onto.create_ontology_from_obo(input_db_dir, files_test["eco_data"])
        list_eco = Onto.parse_eco_terms_from_ontoloy(onto_eco)
        ecos = [cls(data = dict_) for dict_ in list_eco]
        cls.insert_eco_id(ecos,"id")
        cls.insert_name(ecos, "name")
        cls.insert_definition(ecos, "definition")
        cls.save_all()

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for eco in ecos:
                    if 'ancestors' in eco.data.keys():
                        val = eco.__get_ancestors_query()
                        if len(val) != 0:
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

    class Meta():
        table_name = 'eco'

class ECOAncestor(PWModel):
    eco = ForeignKeyField(ECO)
    ancestor = ForeignKeyField(ECO)
    class Meta:
        table_name = 'eco_ancestors'
        database = DbManager.db
        indexes = (
            (('eco', 'ancestor'), True),
        )

class ECOJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.eco_id}},
            "name": {{view_model.model.name}},
            }
        """)

class ECOJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.eco_id}},
            "name": {{view_model.model.name}},
            "ancestors": {{view_model.display_ancestors()}}
            }
        """)

    def display_ancestors(self):
        q = ECOAncestor.select().where(ECOAncestor.eco == self.model.id)
        list_ancestors = []
        for i in range(0, len(q)):
            list_ancestors.append(q[i].ancestor.eco_id)
        return list_ancestors

    