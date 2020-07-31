# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import Resource, ResourceViewModel, DbManager

from biota.prism.ontology import Ontology
from biota._helper.ontology import Onto as OntoHelper

class BTO(Ontology):
    """
    This class represents BTO terms.
    
    The BTO (BRENDA Tissue Ontology) is a comprehensive structured 
    encyclopedia. It providies terms, classifications, and definitions of tissues, organs, anatomical structures, 
    plant parts, cell cultures, cell types, and cell lines of organisms from all taxonomic groups 
    (animals, plants, fungis, protozoon) as enzyme sources (https://www.brenda-enzymes.org/). 
    BRENDA data are available under the Creative Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    :property bto_id: id of the bto term
    :type bto_id: class:`peewee.CharField`
    :property label: label of the bto term
    :type label: class:`peewee.CharField` 
    """
    bto_id = CharField(null=True, index=True)
    label = CharField(null=True, index=True)
    _table_name = 'bto'

    # -- C --

    @classmethod
    def create_table(cls, *arg, **kwargs):
        """
        Creates `bto` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*arg, **kwargs)
        BTOAncestor.create_table()
        
    @classmethod
    def create_bto_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `bto` database

        :param biodata_db_dir: path of the :file:`bto.json`
        :type biodata_db_dir: str
        
        :param files: dictionnary that contains all data files names
        :type files: dict
        """
        list_bto = OntoHelper.parse_bto_from_json(biodata_db_dir, files['bto_json_data'])
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
                    val = bt.__build_insert_query_vals_of_ancestors()
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
        Drops table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        BTOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- G --

    def __build_insert_query_vals_of_ancestors(self):
        """
        Look for the bto term ancestors and returns all bto-bto_ancetors relations in a list.

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
        Remove a bto ancestor.
        """
        Q = BTOAncestor.delete().where(BTOAncestor.bto == self.id, BTOAncestor.ancestor == ancestor.id)
        Q.execute()

    # -- S --

    def set_bto_id(self, bto_id):
        """
        Set the bto_id accessor

        :param: bto_id: The bto_id accessor
        :type bto_id: str
        """
        self.bto_id = bto_id

    def set_label(self, label):
        """
        Set the label

        :param: label: The label
        :type label: str
        """
        self.label = label
  
    class Meta():
        table_name = 'bto'

class BTOAncestor(PWModel):
    """
    This class defines the many-to-many relationship between the bto terms and their ancestors

    :property bto: id of the concerned bto term
    :type bto: CharField 
    
    :property ancestor: ancestor of the concerned bto term
    :type ancestor: CharField 
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

Controller.register_model_classes([BTO])