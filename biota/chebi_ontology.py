from biota.ontology import Ontology
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel
from peewee import CharField
from biota.helper.chebi import Chebi

####################################################################################
#
# Chebi ontology class
#
####################################################################################
 
class ChebiOntology(Ontology):
    chebi_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'chebi_ontology'

    @classmethod
    def create_chebi(cls, input_db_dir, **files):
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