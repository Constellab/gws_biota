from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel
from biota.helper.ontology import Onto
from biota.prism.ontology import Ontology

####################################################################################
#
# SBO class
#
####################################################################################

class SBO(Ontology):
    """

    This class allows to load SBO entities in the database
    Through this class, the user has access to the entire SBO ontology

    SBO terms can be used to introduce a layer of semantic information into the standard 
    description of a model, or to annotate the results of biochemical experiments in order 
    to facilitate their efficient reuse. SBO is an Open Biomedical Ontologies (OBO)
    
    SBO entities are automatically created by the create_sbo() method

    :type sbo_id: CharField 
    :property sbo_id: id of the sbo term
    :type name: CharField 
    :property name: name of the sbo term
    :type namespace: CharField 
    :property namespace: namespace of the go term

    """
    sbo_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'sbo'

    # -- C --
     
    @classmethod
    def create_sbo(cls, input_db_dir, **files):
        """

        This method allows biota module to create GO entities

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the sboo.obo file
        :type files_test: dict
        :param files_test: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """
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
        """

        Creates tables related to SBO entities such as sbo, sbo ancestors, etc...
        Uses the super() method of the gws.model object to create the sbo table

        """
        super().create_table(*arg, **kwargs)
        SBOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        """

        returns self.definition

        """
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        
        Drops tables related to SBO entities such as sbo, sbo ancestors, etc...
        Uses the super() method of the gws.model object to drop the sbo table

        """
        SBOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S --

    def set_name(self, name__):
        """

        set self.sbo_id
        
        """
        self.name = name__    

    def set_sbo_id(self, id):
        """

        set self.name
        
        """
        self.sbo_id = id
    
    def _get_ancestors_query(self):
        """

        look for the sbo term ancestors and returns all sbo-sbo_ancestors relations in a list 
        :returns: a list of dictionnaries inf the following format: {'sbo': self.id, 'ancestor': ancestor.id}
        :rtype: list
        
        """
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.sbo_id):
                val = {'sbo': self.id, 'ancestor': SBO.get(SBO.sbo_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)

    class Meta():
        table_name = 'sbo'

class SBOAncestor(PWModel):
    """
    
    This class refers to sbo ancestors, which are sbo entities but also parent of sbo element

    SBOAncestor entities are created by the create_sbo() method which get ancestors of the sbo term by
    calling __get_ancestors_query()

    :type sbo: CharField 
    :property sbo: id of the concerned sbo term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned sbo term
    
    """
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