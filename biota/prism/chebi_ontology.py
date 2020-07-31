# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com
#
# ChEBI Copyright Notice and License:
# ChEBI data are available under the Creative Commons License (CC BY 4.0).
# The Creative Commons Attribution License CC BY 4.0 
# is applied to all copyrightable parts of BRENDA. 
# The copyrightable parts of BRENDA are copyright-protected by Prof. Dr. D. Schomburg, Technische 
# Universität Braunschweig, BRICS,Department of Bioinformatics and Biochemistry, 
# Rebenring 56, 38106 Braunschweig, Germany.
# https://www.brenda-enzymes.org
#
# Attribution 4.0 International (CC BY 4.0) information, 2020:
# You are free to:
# * Share — copy and redistribute the material in any medium or format
# * Adapt — remix, transform, and build upon the material
#     for any purpose, even commercially.
# This license is acceptable for Free Cultural Works.
# The licensor cannot revoke these freedoms as long as you follow the license terms.
# https://creativecommons.org/licenses/by/4.0/.

from peewee import CharField

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import Resource, ResourceViewModel

from biota.prism.ontology import Ontology
from biota._helper.chebi import Chebi as ChebiHelper

class ChebiOntology(Ontology):
    """
    This class represents ChEBI Ontology terms.
    
    Chemical Entities of Biological Interest (ChEBI) includes an ontological classification, whereby the 
    relationships between molecular entities or classes of entities and their parents and/or children are 
    specified (https://www.ebi.ac.uk/chebi/). ChEBI data are available under the Creative Commons License (CC BY 4.0),
    https://creativecommons.org/licenses/by/4.0/


    :property chebi_id: id of the ChEBI term
    :type chebi_id: class:`peewee.CharField`
    :property name: name of the ChEBI term
    :type name: class:`peewee.CharField`
    """

    chebi_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'chebi_ontology'

    @classmethod
    def create_chebi_ontology_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `chebi_ontology` database

        :type biodata_db_dir: str
        :param biodata_db_dir: path of the :file:`chebi.obo`
        :type files: dict
        :param files: dictionnary that contains all data files names
        :returns: None
        :rtype: None
        """
        onto = ChebiHelper.create_ontology_from_file(biodata_db_dir, files['chebi_data'])
        list_chebi = ChebiHelper.parse_onto_from_ontology(onto)
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

Controller.register_model_classes([ChebiOntology])