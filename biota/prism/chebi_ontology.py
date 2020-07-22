from biota.prism.ontology import Ontology
from biota.helper.chebi import Chebi
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel
from peewee import CharField


####################################################################################
#
# Chebi ontology class
#
####################################################################################
 
class ChebiOntology(Ontology):
    """

    This class allows to load Chebi Ontology entities in the database
    Through this class, the biota has access to the entire Chebi ontology

    Chemical Entities of Biological Interest (ChEBI) includes an
    ontological classification, whereby the relationships between molecular 
    entities or classes of entities and their parents and/or children are specified
    
    Chebi entities are automatically created by the create_chebi() method

    :type chebi_id: CharField 
    :property chebi_id: id of the chebi term
    :type name: CharField 
    :property name: name of the chebi term

    """
    chebi_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'chebi_ontology'

    @classmethod
    def create_chebi(cls, input_db_dir, **files):
        """

        This method allows the biota module to create chebi entities

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the chebi.obo file
        :type files_test: dict
        :param files_test: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """
        onto = Chebi.create_ontology_from_file(input_db_dir, files['chebi_data'])
        list_chebi = Chebi.parse_onto_from_ontology(onto)
        chebis = [cls(data = dict_) for dict_ in list_chebi]

        for chebi in chebis:
            chebi.name = chebi.data["name"]
            chebi.chebi_id = chebi.data["id"]

        cls.save_all(chebis)
        return(list_chebi)

    class Meta():
        table_name = 'chebi_ontology'

class ChebiOntologyStandardJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.chebi_id}},
            "label": {{view_model.model.name}},
            }
        """)

class ChebiOntologyPremiumJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.chebi_id}},
            "label": {{view_model.model.name}},
            "definition": {{view_model.model.data["definition"]}},
            "alternative_id": {{view_model.model.data["alt_id"]}}
            }
        """)