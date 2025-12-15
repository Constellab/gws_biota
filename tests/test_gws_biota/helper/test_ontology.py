import os
import unittest

from gws_biota._helper.ontology import Onto
from gws_core import Settings


class TestOntology(unittest.TestCase):
    def test_db_object(self):
        settings = Settings.get_instance()
        testdata_path = os.path.join(
            settings.get_variable("gws_biota", "testdata_dir"), "../_helper/data/"
        )

        #### Test go parser ####
        file = "go_test.obo"
        ontology = Onto.create_ontology_from_obo(testdata_path, file)
        list_go = Onto.parse_obo_from_ontology(ontology)
        self.assertEqual(len(list_go), 14)
        self.assertEqual(list_go[0]["id"], "GO:0000001")
        self.assertEqual(list_go[1]["id"], "GO:0000002")
        self.assertEqual(len(list_go[9]["ancestors"]), 1)

        #### Test sbo parser ####
        file = "sbo_test.obo"
        sbo_path, file_name = Onto.correction_of_sbo_file(testdata_path, file)
        ontology = Onto.create_ontology_from_obo(sbo_path, file_name)
        list_sbo_terms = Onto.parse_sbo_terms_from_ontology(ontology)
        self.assertEqual(len(list_sbo_terms), 21)
        self.assertEqual(list_sbo_terms[0]["id"], "SBO:0000000")

        #### Test BTO parser ####
        file = "bto_test.obo"
        ontology = Onto.create_ontology_from_file(testdata_path, file)
        list_bto = Onto.parse_bto_from_ontology(ontology)
        self.assertEqual(len(list_bto), 20)
        self.assertEqual(
            list_bto[0],
            {
                "id": "BTO:0000000",
                "name": "tissues, cell types and enzyme sources",
                "definition": "A structured controlled vocabulary for the source of an enzyme. It comprises terms of tissues, cell lines, cell types and cell cultures from uni- and multicellular organisms.",
                "synonyms": [],
                "ancestors": ["BTO:0000000"],
            },
        )
        self.assertEqual(
            list_bto[1],
            {
                "id": "BTO:0000001",
                "name": "culture condition:-induced cell",
                "definition": "None",
                "synonyms": [],
                "ancestors": ["BTO:0000001", "BTO:0000216"],
            },
        )

        #### Test ECO parser ####
        file = "eco_test.obo"
        ontology = Onto.create_ontology_from_obo(testdata_path, file)
        list_eco = Onto.parse_eco_terms_from_ontoloy(ontology)
        self.assertEqual(len(list_eco), 25)
        self.assertEqual(
            list_eco[0],
            {
                "id": "ECO:0000000",
                "name": "evidence",
                "definition": "A type of information that is used to support an assertion.",
            },
        )

        self.assertEqual(
            list_eco[10],
            {
                "id": "ECO:0000010",
                "name": "protein expression evidence",
                "definition": "A type of expression pattern evidence resulting from protein abundance quantification techniques.",
                "ancestors": ["ECO:0000002"],
            },
        )

        #### Test pwo parser ####
        file = "pwo_test.obo"
        pwo_path, file_name = Onto.correction_of_pwo_file(testdata_path, file)
        ontology = Onto.create_ontology_from_obo(pwo_path, file_name)
        list_pwo = Onto.parse_pwo_terms_from_ontology(ontology)
        self.assertEqual(len(list_pwo), 34)
        self.assertEqual(
            list_pwo[0], {"id": "PW:0000000", "name": "term zero", "definition": "None"}
        )
        self.assertEqual(
            list_pwo[10],
            {
                "id": "PW:0000010",
                "name": "lipid metabolic pathway",
                "definition": "The metabolic reactions involved in the oxidation, utilization and/or synthesis of lipids in the tissues.",
                "ancestors": ["PW:0000002"],
            },
        )
