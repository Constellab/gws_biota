from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.prism.ontology import Ontology
from biota.helper.ontology import Onto

####################################################################################
#
# BTO class
#
####################################################################################

class BTO(Ontology):
    bto_id = CharField(null=True, index=True)
    label = CharField(null=True, index=True)
    _table_name = 'bto'

    # -- A --

    @property
    def ancestors(self):
        Q = BTOAncestor.select(BTOAncestor.bto == self.id)
        ancestors = []
        for ancestor in Q:
            ancestors.append(ancestor)
        return ancestors

    def add_ancestor(self, ancestor):
        BTOAncestor.create(bto = self, ancestor = ancestor)

    # -- C --

    @classmethod
    def create_table(cls, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        BTOAncestor.create_table()

    @classmethod
    def create_bto(cls, input_db_dir, **files):
        list_bto = Onto.parse_bto_from_json(input_db_dir, files['bto_json_data'])
        btos = [cls(data = dict_) for dict_ in list_bto]

        for bto in btos:
            bto.set_bto_id( bto.data["id"] )
            bto.set_label( bto.data["label"] )

        cls.save_all(btos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for bt in btos:
                    val = bt._get_ancestors_query()
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
        BTOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- G --

    def _get_ancestors_query(self):
        vals = []
        for i in range(0,len(self.data['ancestors'])):
            if (self.data['ancestors'][i] != self.bto_id):
                val = {'bto': self.id, 'ancestor': BTO.get(BTO.bto_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return vals
        
    # -- R --

    def remove_ancestor(self, ancestor):
        Q = BTOAncestor.delete().where(BTOAncestor.bto == self.id, BTOAncestor.ancestor == ancestor.id)
        Q.execute()

    # -- S --

    def set_bto_id(self, bto_id):
        self.bto_id = bto_id

    def set_label(self, label):
        self.label = label
  
    class Meta():
        table_name = 'bto'

class BTOAncestor(PWModel):
    bto = ForeignKeyField(BTO)
    ancestor = ForeignKeyField(BTO)
    class Meta:
        table_name = 'bto_ancestors'
        database = DbManager.db
        indexes = (
            (('bto', 'ancestor'), True),
        )

class BTOJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.bto_id}}, 
            "label": {{view_model.model.label}},
            }
        """)

class BTOJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.bto_id}}, 
            "label": {{view_model.model.label}},
            "ancestors" : {{view_model.display_ancestors()}},
            }
        """)
    
    def display_ancestors(self):
        q = BTOAncestor.select().where(BTOAncestor.bto == self.model.id)
        list_ancestors = []
        for i in range(0, len(q)):
            list_ancestors.append(q[i].ancestor.bto_id)
        return(list_ancestors)
