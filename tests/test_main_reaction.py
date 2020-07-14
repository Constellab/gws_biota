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
from biota.chebiOntology import ChebiOntology
from biota.taxonomy import Taxonomy
from biota.compound import Compound
from biota.enzyme import Enzyme
from biota.reaction import Reaction

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
#                                        class test_main_reaction
#                                         
###########################################################################################
settings = Settings.retrieve()
enzyme_bto = Enzyme.bto.get_through_model()

files_model = dict(
    substrate_reaction = Reaction.substrates.get_through_model(),
    product_reaction = Reaction.products.get_through_model(),
    enzyme_reaction = Reaction.enzymes.get_through_model()
    )

class TestMain(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        # --- drops --- #
        BTO.drop_table()
        ChebiOntology.drop_table()
        Compound.drop_table()
        Enzyme.drop_table()
        enzyme_bto.drop_table()
        Reaction.drop_table(**files_model)
        # --- creations --- #
        BTO.create_table()
        Compound.create_table()
        Enzyme.create_table()
        enzyme_bto.create_table()
        Reaction.create_table(**files_model)
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
            chebi_data = "chebi.obo",
            bto_json_data = "bto.json",
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file =  "chemical_data.tsv",
            brenda_file = "brenda_download_20200504.txt",
            rhea_kegg_reaction_file =  'rhea-kegg.reaction',
            rhea_direction_file = 'rhea-directions.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc.tsv',
            rhea2metacyc_file = 'rhea2metacyc.tsv',
            rhea2macie_file = 'rhea2macie.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction.tsv',
            rhea2ec_file = 'rhea2ec.tsv',
            rhea2reactome_file = 'rhea2reactome.tsv'
        )

        start = default_timer()

        # ------------- Create BTO ------------- #
        bto_input_db_dir = settings.get_data("bto_input_db_dir")
        BTO.create_bto(bto_input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')
        duration  = default_timer() - start
        print("bto and bto_ancestors have been loaded in " + str(duration) + " sec")

        # ------------- Create ChebiOntology ------------- #
        chebi_input_db_dir = settings.get_data("chebi_input_db_dir")
        ChebiOntology.create_chebis(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        duration  = default_timer() - duration
        print("chebiOntology has been loaded in " + str(duration) + " sec")

        # ------------- Create Compound ------------- #
        chebi_input_db_dir = settings.get_data("chebi_input_db_dir")
        Compound.create_compounds_from_files(chebi_input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(Compound.get(Compound.source_accession == 'CHEBI:58321').name, 'L-allysine zwitterion')
        duration  = default_timer() - duration
        print("compound has been loaded in " + str(duration) + " sec")

        # ------------- Create Enzyme ------------- #
        brenda_texfile_input_db_dir = settings.get_data("brenda_texfile_input_db_dir")
        Enzyme.create_enzymes_from_dict(brenda_texfile_input_db_dir, **files)
        Controller.save_all()
        duration  = default_timer() - duration
        print("enzyme and enzyme_btos have been loaded in " + str(duration) + " sec")

        # ------------- Create Reactions ------------- #
        rhea_input_db_dir = settings.get_data("rhea_input_db_dir")
        Reaction.create_reactions_from_files(rhea_input_db_dir, **files)
        rea1 = Reaction.get(Reaction.source_accession == 'RHEA:10031')
        duration  = default_timer() - duration
        print("reactions, reactions_enzymes, reactions_substrates and reactions_products have been loaded in " + str(duration) + " sec")