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
from biota.go import GO, GOJSONViewModel
from biota.sbo import SBO, SBOJSONViewModel
from biota.bto import BTO, BTOJSONViewModel
from biota.chebiOntology import ChebiOntology, ChebiOntologyJSONViewModel
from biota.taxonomy import Taxonomy, TaxonomyJSONViewModel
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
#                                        class test_main_admin
#                                         
############################################################################################
input_db_dir = settings.get_data("biota_db_input_path")

class TestMain(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        GO.drop_table()
        SBO.drop_table()
        BTO.drop_table()
        Taxonomy.drop_table()
        ChebiOntology.drop_table()
        GOJSONViewModel.drop_table()
        GO.create_table()
        SBO.create_table()
        BTO.create_table()
        Taxonomy.create_table()
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
            sbo_data = "SBO_OBO.obo",
            chebi_data = "chebi.obo",
            bto_json_data = "bto.json",
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file =  "chemical_data.tsv",
            brenda_file = "brenda_download.txt",
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
        go1 = GO.get(GO.go_id == 'GO:0000001')
        go1_view_model = GOJSONViewModel(go1)
        Controller.save_all()
        view = go1_view_model.render()
        self.assertEqual(view, '{"id": GO:0000001 , "name": mitochondrion inheritance, "namespace": biological_process , "definition": The distribution of mitochondria, including the mitochondrial genome, into daughter cells after mitosis or meiosis, mediated by interactions between mitochondria and the cytoskeleton. }')
        duration  = default_timer() - start
        print("go, go_ancestors and gojsonviewmodel have been loaded in " + str(duration) + " sec")

        # ------------- Create SBO ------------- #
        SBO.create_sbo(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(SBO.get(SBO.sbo_id == 'SBO:0000000').name, 'systems biology representation')
        self.assertEqual(SBO.get(SBO.sbo_id == "SBO:0000005").name, 'obsolete mathematical expression')

        sbo1 = SBO.get(SBO.sbo_id == 'SBO:0000000')
        sbo1_view_model = SBOJSONViewModel(sbo1)
        Controller.save_all()
        view = sbo1_view_model.render()
        self.assertEqual(view, '{"id": SBO:0000000 , "name": systems biology representation, "definition": Representation of an entity used in a systems biology knowledge reconstruction, such as a model, pathway, network. }')
        duration  = default_timer() - duration
        print("sbo, sbo_ancestors and ressourceviewmodel have been loaded in " + str(duration) +  " sec")

        # ------------- Create BTO ------------- #
        BTO.create_bto(input_db_dir, **files)
        Controller.save_all()
        self.assertEqual(BTO.get(BTO.bto_id == 'BTO_0000000').label, 'tissues, cell types and enzyme sources')
        bto1 = BTO.get(BTO.bto_id == 'BTO_0000000')
        bto1_view_model = BTOJSONViewModel(bto1)
        Controller.save_all()
        view = bto1_view_model.render()
        duration  = default_timer() - duration
        print("bto and bto_ancestors have been loaded in " + str(duration) + " sec")

        # ------------- Create ChebiOntology ------------- #
        ChebiOntology.create_chebis(input_db_dir, **files)
        Controller.save_all()
        #self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        #self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        chebi1 = ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431')
        chebi1_view_model = ChebiOntologyJSONViewModel(chebi1)
        view = chebi1_view_model.render()
        self.assertEqual(view, '{"chebi_id": CHEBI:24431 , "name": chemical entity, "definition": A chemical entity is a physical entity of interest in chemistry including molecular entities, parts thereof, and chemical substances. }')
        duration  = default_timer() - duration
        print("chebiOntology has been loaded in " + str(duration) + " sec")

        # ------------- Create Taxonomy ------------- #
        dict_taxons = Taxonomy.create_taxons_from_dict()
        Controller.save_all()
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 41297).name, "Sphingomonadaceae")
        tax1 = Taxonomy.get(Taxonomy.tax_id == 41297)
        tax1_view_model = TaxonomyJSONViewModel(tax1)
        view = tax1_view_model.render()
        self.assertEqual(view, '{"tax_id": 41297 , "name": Sphingomonadaceae, "rank": family , "ancestors": [] }')