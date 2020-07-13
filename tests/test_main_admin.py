import sys
import os
import unittest
import copy
import asyncio

#import from gws
from gws.prism.app import App
from gws.prism.model import Process, Resource
from gws.prism.controller import Controller


#import from pewee
from peewee import CharField, ForeignKeyField, chunked
from peewee import CharField, ForeignKeyField, chunked

#import from starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

#import from biota
from manage import settings
from biota.go import GO
from biota.sbo import SBO
from biota.bto import BTO
from biota.chebiOntology import ChebiOntology
from biota.taxonomy import Taxonomy
from biota.compound import Compound
from biota.enzyme import Enzyme
from biota.enzymeAnnotation import EnzymeAnnotation
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
#                                        class test_main_admin
#                                         
############################################################################################
input_db_dir = settings.get_data("biota_db_input_path")
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
        GO.drop_table()
        SBO.drop_table()
        BTO.drop_table()
        ChebiOntology.drop_table()
        Taxonomy.drop_table()
        Compound.drop_table()
        Enzyme.drop_table()
        EnzymeAnnotation.drop_table()
        enzyme_bto.drop_table()
        Reaction.drop_table(**files_model)
        # --- creations --- #
        GO.create_table()
        SBO.create_table()
        BTO.create_table()
        ChebiOntology.create_table()
        Taxonomy.create_table()
        Compound.create_table()
        Enzyme.create_table()
        EnzymeAnnotation.create_table()
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
            sbo_data = "SBO_OBO.obo",
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
            rhea2ec_file = 'rhea2ec.tsv'
        )

        start = default_timer()
        # ------------- Create GO ------------- #
        GO.create_go(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').name, "mitochondrion inheritance")
        duration  = default_timer() - start
        print("go, go_ancestors and gojsonviewmodel have been loaded in " + str(duration) + " sec")

        # ------------- Create SBO ------------- #
        SBO.create_sbo(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(SBO.get(SBO.sbo_id == 'SBO:0000000').name, 'systems biology representation')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000005").name, 'obsolete mathematical expression')
        
        duration  = default_timer() - duration
        print("sbo, sbo_ancestors and ressourceviewmodel have been loaded in " + str(duration) +  " sec")

        # ------------- Create BTO ------------- #
        BTO.create_bto(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')
        duration  = default_timer() - duration
        print("bto and bto_ancestors have been loaded in " + str(duration) + " sec")

        # ------------- Create ECO ------------- #
        ECO.create_eco(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').name, "inference from background scientific knowledge")
        duration  = default_timer() - duration
        print("eco and eco_ancestors have been loaded in " + str(duration) + " sec")

        # ------------- Create ChebiOntology ------------- #
        ChebiOntology.create_chebis(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        duration  = default_timer() - duration
        print("chebiOntology has been loaded in " + str(duration) + " sec")

        """
        # ------------- Create Taxonomy ------------- #
        Taxonomy.create_taxons_from_dict(['Eukaryota'])
        #self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 41297).name, "Sphingomonadaceae")
        duration  = default_timer() - duration
        print("taxonomy has been loaded in " + str(duration) + " sec")
        """
        
        # ------------- Create Compound ------------- #
        Compound.create_compounds_from_files(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(Compound.get(Compound.source_accession == 'CHEBI:58321').name, 'L-allysine zwitterion')
        duration  = default_timer() - duration
        print("compound has been loaded in " + str(duration) + " sec")

        # ------------- Create Enzyme ------------- #
        Enzyme.create_enzymes_from_dict(input_db_dir, **files)
        Controller.save_all()
        duration  = default_timer() - duration
        print("enzyme and enzyme_btos have been loaded in " + str(duration) + " sec")

        # ------------- Create EnzymeAnnotation ------------- #
        EnzymeAnnotation.create_annotation()
        duration  = default_timer() - duration
        print("enzymeAnnotation has been loaded in " + str(duration) + " sec")
        
        """
        # ------------- Create Reactions ------------- #
        Reaction.create_reactions_from_files(input_db_dir, **files)
        rea1 = Reaction.get(Reaction.source_accession == 'RHEA:10031')
        print("reactions, reactions_enzymes, reactions_substrates and reactions_products have been loaded in " + str(duration) + " sec")
        """