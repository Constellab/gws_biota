import sys
import os
import unittest
import copy
import asyncio

#import from gws
from gws.prism.controller import Controller

#import from biota
from gws.settings import Settings
from biota.go import GO
from biota.sbo import SBO
from biota.bto import BTO
from biota.eco import ECO
from biota.chebiOntology import ChebiOntology


#import external module 
from rhea.rhea import Rhea
from brenda.brenda import Brenda
from onto.ontology import Onto
from chebi.chebi import Chebi
from taxo.taxonomy import Taxo

#import Timer
from timeit import default_timer

############################################################################################
#
#                                        class test_main_ontology
#                                         
############################################################################################
settings = Settings.retrieve()
class TestMain(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        # --- drops --- #
        GO.drop_table()
        SBO.drop_table()
        BTO.drop_table()
        ECO.drop_table()
        ChebiOntology.drop_table()
        # --- creations --- #
        GO.create_table()
        SBO.create_table()
        BTO.create_table()
        ECO.create_table()
        ChebiOntology.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        #GO.drop_table()
        #SBO.drop_table()
        #BTO.drop_table()
        #ChebiOntology.drop_table()
        pass
    
    def test_db_object(self):
        files = dict(
            go_data = "go.obo",
            sbo_data = "sbo.obo",
            eco_data = "eco.obo",
            chebi_data = "chebi.obo",
            bto_json_data = "bto.json",
            eco_data = 'eco.obo',
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file =  "chemical_data.tsv",
            brenda_file = "brenda_download_20200504.txt",
            rhea_kegg_reaction_file =  'rhea-kegg.reaction',
            rhea_direction_file = 'rhea-directions.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc.tsv',
            rhea2metacyc_file = 'rhea2metacyc.tsv',
            rhea2macie_file = 'rhea2macie.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction.tsv',
            rhea2ec_file = 'rhea2ec.tsv'
        )

        start = default_timer()
        
        # ------------- Create GO ------------- #
        go_input_db_dir = settings.get_data("go_input_db_dir")
        GO.create_go(go_input_db_dir, **files)
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').name, "mitochondrion inheritance")
        duration  = default_timer() - start
        print("go, go_ancestors and gojsonviewmodel have been loaded in " + str(duration) + " sec")

        # ------------- Create SBO ------------- #
        sbo_input_db_dir = settings.get_data("sbo_input_db_dir")
        SBO.create_sbo(sbo_input_db_dir, **files)
        self.assertEqual(SBO.get(SBO.sbo_id == 'SBO:0000000').name, 'systems biology representation')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000005").name, 'obsolete mathematical expression')
        
        duration  = default_timer() - duration
        print("sbo, sbo_ancestors and ressourceviewmodel have been loaded in " + str(duration) +  " sec")
        
        # ------------- Create BTO ------------- #
        bto_input_db_dir = settings.get_data("bto_input_db_dir")
        BTO.create_bto(bto_input_db_dir, **files)
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')
        duration  = default_timer() - duration
        print("bto and bto_ancestors have been loaded in " + str(duration) + " sec")
        
        # ------------- Create ECO ------------- #
        eco_input_db_dir = settings.get_data("eco_input_db_dir")
        ECO.create_eco(eco_input_db_dir, **files)
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').name, "inference from background scientific knowledge")
        duration  = default_timer() - duration
        print("eco and eco_ancestors have been loaded in " + str(duration) + " sec")
        
        # ------------- Create ChebiOntology ------------- #
        chebi_input_db_dir = settings.get_data("chebi_input_db_dir")
        ChebiOntology.create_chebi(chebi_input_db_dir, **files)
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        duration  = default_timer() - duration
        print("chebiOntology has been loaded in " + str(duration) + " sec")