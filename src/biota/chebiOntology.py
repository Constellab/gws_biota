from biota.ontology import Ontology
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel
from peewee import CharField
from chebi.chebi import Chebi

####################################################################################
#
# Chebi ontology class
#
####################################################################################
 
class ChebiOntology(Ontology):
    chebi_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    #definition = CharField(null=True, index=True)
    #xrefs = CharField(null=True, index=True)
    _table_name = 'chebi_ontology'

    #Setters
    def set_chebi_id(self, id):
        self.chebi_id = id
    
    def set_name(self, name):
        self.name = name
    
    #Inserts
    @classmethod
    def insert_chebi_id(cls, list__, key):
        for chebs in list__:
            chebs.set_chebi_id(chebs.data[key])

    @classmethod
    def insert_name(cls, list__, key):
        for chebs in list__:
            chebs.set_name(chebs.data[key])

    @classmethod
    def create_chebis(cls, input_db_dir, **files):
        onto = Chebi.create_ontology_from_file(input_db_dir, files['chebi_data'])
        list_chebi = Chebi.parse_onto_from_ontology(onto)
        chebis = [cls(data = dict_) for dict_ in list_chebi]
        cls.insert_chebi_id(chebis, "id")
        cls.insert_name(chebis, "name")
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