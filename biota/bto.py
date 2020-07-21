from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.ontology import Ontology
from biota.helper.ontology import Onto

####################################################################################
#
# BTO class
#
####################################################################################

class BTO(Ontology):
    """

    This class allows to load BTO entities in the database
    Through this class, the user has access to the entire BTO ontology

    The BTO (BRENDA Tissue Ontology) represents a comprehensive structured encyclopedia. 
    It provides terms, classifications, and definitions of tissues, organs, anatomical structures, 
    plant parts, cell cultures, cell types, and cell lines of organisms from all taxonomic groups 
    (animals, plants, fungis, protozoon) as enzyme sources. The information is connected to the 
    functional data in the BRENDA ("BRaunschweig ENzyme DAtabase“) enzyme information system. 
    
    BTO entities are automatically created by the create_bto() method

    :type bto_id: CharField 
    :property bto_id: id of the bto term
    :type label: CharField 
    :property label: label of the bto term

    """
    bto_id = CharField(null=True, index=True)
    label = CharField(null=True, index=True)
    _table_name = 'bto'

    # -- C --

    @classmethod
    def create_table(cls, *arg, **kwargs):
        """

        Creates tables related to BTO entities such as bto, bto ancestors, etc...
        Uses the super() method of the gws.model object to create the bto table

        """
        super().create_table(*arg, **kwargs)
        BTOAncestor.create_table()
    # -- C --
    @classmethod
    def create_bto(cls, input_db_dir, **files):
        """

        This method allows the biota module to create BTO entities

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the bto.json file
        :type files_test: dict
        :param files_test: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """
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
        """
        
        Drops tables related to BTO entities such as bto, bto ancestors, etc...
        Uses the super() method of the gws.model object to drop the bto table

        """
        BTOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- G --

    def _get_ancestors_query(self):
        """

        look for the bto term ancestors and returns all bto-bto_ancetors relations in a list 
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

    def remove_ancestor(self, ancestor):
        """

        remove bto-bto_ancestors relations of the bto_ancestors table whose ancestors is the ancestor parameter
        
        """
        Q = BTOAncestor.delete().where(BTOAncestor.bto == self.id, BTOAncestor.ancestor == ancestor.id)
        Q.execute()

    # -- S --

    def set_bto_id(self, bto_id):
        """
        set self.bto_id
        """
        self.bto_id = bto_id

    def set_label(self, label):
        """
        set self.label
        """
        self.label = label
  
    class Meta():
        table_name = 'bto'

class BTOAncestor(PWModel):
    """
    
    This class refers to bto ancestors, which are bto entities but also parent of bto element

    SBOAncestor entities are created by the create_bto() method which get ancestors of the bto term by
    calling __get_ancestors_query()

    :type bto: CharField 
    :property bto: id of the concerned bto term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned bto term
    
    """
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
