# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager

from biota._helper.ontology import Onto as OntoHelper
from biota.db.ontology import Ontology

class SBO(Ontology):
    """
    This class represents SBO terms.

    The SBO (Systems Biology Ontology) is a set of controlled, relational vocabularies 
    of terms commonly used in Systems Biology, and in particular in computational modelling.
    It introduce a layer of semantic information into the standard description of a model, 
    or to annotate the results of biochemical experiments in order to facilitate their efficient reuse
    (http://www.ebi.ac.uk/sbo). SBO is under the Artistic License 2.0 (https://opensource.org/licenses/Artistic-2.0)

    :property sbo_id: id of the sbo term
    :type sbo_id: class:`peewee.CharField` 
    :property name: name of the sbo term
    :type name: class:`peewee.CharField` 
    """

    sbo_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'sbo'

    # -- C --
     
    @classmethod
    def create_sbo_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `sbo` database

        :param biodata_db_dir: path to the folder that contain the :file:`sbo.obo` file
        :type biodata_db_dir: str
        :param files_test: dictionnary that contains all data files names
        :type files_test: dict
        :returns: None
        :rtype: None
        """

        OntoHelper.correction_of_sbo_file(biodata_db_dir, files["sbo_data"], 'sbo_out_test.obo')
        ontology = OntoHelper.create_ontology_from_obo(biodata_db_dir, 'sbo_out_test.obo')
        list_sbo = OntoHelper.parse_sbo_terms_from_ontology(ontology)

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
                        val = sbo.__build_insert_query_vals_of_ancestors()
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
        Creates `sbo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*arg, **kwargs)
        SBOAncestor.create_table()

    # -- D --

    @property
    def definition(self):
        """
        Returns the definition of the got term

        :returns: The definition
        :rtype: str
        """
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `sbo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        SBOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S --

    def set_name(self, name__):
        """
        Sets the name of the sbo term

        :param name: The name
        :type name: str
        """
        self.name = name__    

    def set_sbo_id(self, sbo_id):
        """
        Sets the sbo id of the sbo term

        :param sbo_id: The sbo id
        :type sbo_id: str
        """
        self.sbo_id = sbo_id
    
    def __build_insert_query_vals_of_ancestors(self):
        """
        Look for the sbo term ancestors and returns all sbo-sbo_ancestors relations in a list.

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
    This class defines the many-to-many relationship between the sbo terms and theirs ancestors

    :property sbo: id of the concerned sbo term
    :type sbo: CharField 
    :property ancestor: ancestor of the concerned sbo term
    :type ancestor: CharField 
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

Controller.register_model_classes([SBO])