from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import Model, ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.ontology import Ontology
from biota.helper.ontology import Onto

####################################################################################
#
# ECO class
#
####################################################################################

class ECO(Ontology):
    """

    This class allows to load ECO entities in the database
    Through this class, the biota has access to the entire ECO ontology

    The Evidence and Conclusion Ontology (ECO) contains terms (classes) that describe 
    types of evidence and assertion methods. ECO terms are used in the process of 
    biocuration to capture the evidence that supports biological assertions 
    (e.g. gene product X has function Y as supported by evidence Z) 
    
    ECO entities are automatically created by the create_eco() method

    :type eco_id: CharField 
    :property eco_id: id of the eco term
    :type name: CharField 
    :property name: name of the eco term

    """

    eco_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'eco'

    # -- C --

    @classmethod
    def create_table(cls, *arg, **kwargs):
        """

        Creates tables related to ECO entities such as eco, eco ancestors, etc...
        Uses the super() method of the gws.model object to create the eco table

        """
        super().create_table(*arg, **kwargs)
        ECOAncestor.create_table()

    @classmethod
    def create_eco(cls, input_db_dir, **files_test):
        """

        This method allows the biota module to create ECO entities

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the eco.obo file
        :type files_test: dict
        :param files_test: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """

        onto_eco = Onto.create_ontology_from_obo(input_db_dir, files_test["eco_data"])
        list_eco = Onto.parse_eco_terms_from_ontoloy(onto_eco)
        ecos = [cls(data = dict_) for dict_ in list_eco]

        for eco in ecos:
            eco.set_eco_id( eco.data["id"] )
            eco.set_name( eco.data["name"] )

        cls.save_all(ecos)

        vals = []
        bulk_size = 100

        with DbManager.db.atomic() as transaction:
            try:
                for eco in ecos:
                    if 'ancestors' in eco.data.keys():
                        val = eco._get_ancestors_query()
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

    # -- D --

    
    @property
    def definition(self):
        """
        return self.definition
        """
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        
        Drops tables related to ECO entities such as eco, eco ancestors, etc...
        Uses the super() method of the gws.model object to drop the eco table

        """
        ECOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
    

    # -- G --

    def _get_ancestors_query(self):
        """

        look for the eco term ancestors and returns all eco-eco_ancetors relations in a list 
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

    def set_name(self, name__):
        """
        set self.name
        """
        self.name = name__

    class Meta():
        table_name = 'eco'

class ECOAncestor(PWModel):
    """
    
    This class refers to eco ancestors, which are eco entities but also parent of eco element

    ECOAncestor entities are created by the create_eco() method which get ancestors of the eco term by
    calling __get_ancestors_query()

    :type eco: CharField 
    :property eco: id of the concerned eco term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned eco term
    
    """
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

    