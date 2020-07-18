from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.helper.ontology import Onto
from biota.ontology import Ontology

####################################################################################
#
# SBO class
#
####################################################################################

class SBO(Ontology):
    sbo_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'sbo'

    # -- C --
     
    @classmethod
    def create_sbo(cls, input_db_dir, **files):
        Onto.correction_of_sbo_file(input_db_dir, files["sbo_data"], 'sbo_out_test.obo')
        ontology = Onto.create_ontology_from_owl(input_db_dir, 'sbo_out_test.obo')
        list_sbo = Onto.parse_sbo_terms_from_ontology(ontology)

        sbos = [cls(data = dict_) for dict_ in list_sbo]
        for sbo in sbos:
            sbo.set_sbo_id(sbo.data["id"])
            sbo.set_name(sbo.data["name"])

        cls.save_all(sbos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for sbo in sbos:
                    if 'ancestors' in sbo.data.keys():
                        val = sbo._get_ancestors_query()
                        if len(val) != 0:
                            for v in val:
                                vals.append(v)
                                if len(vals) == bulk_size:
                                    SBOAncestor.insert_many(vals).execute()
                                    vals = []
                            
                            if len(vals) != 0:
                                SBOAncestor.insert_many(vals).execute()
                                vals = []

            except:
                transaction.rollback()

    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        SBOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        SBOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S --

    def set_name(self, name__):
        self.name = name__    

    def set_sbo_id(self, id):
        self.sbo_id = id
    
    def _get_ancestors_query(self):
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.sbo_id):
                val = {'sbo': self.id, 'ancestor': SBO.get(SBO.sbo_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)

    class Meta():
        table_name = 'sbo'

class SBOAncestor(PWModel):
    sbo = ForeignKeyField(SBO)
    ancestor = ForeignKeyField(SBO)
    class Meta:
        table_name = 'sbo_ancestors'
        database = DbManager.db
        indexes = (
            (('sbo', 'ancestor'), True),
        )

class SBOStandardJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.sbo_id}},
            "name": {{view_model.model.name}}
            }
        """)
class SBOPremiumJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.sbo_id}},
            "name": {{view_model.model.name}},
            "definition": {{view_model.model.definition}},
            "ancestors": {{view_model.display_ancestors()}}
            }
        """)
    
    def display_ancestors(self):
        q = SBOAncestor.select().where(SBOAncestor.sbo == self.model.id)
        list_ancestors = []
        for i in range(0, len(q)):
            list_ancestors.append(q[i].ancestor.sbo_id)
        return list_ancestors