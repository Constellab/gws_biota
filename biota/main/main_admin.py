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
from biota.compound import Compound
from biota.reaction import Reaction
from biota.enzyme import Enzyme
from biota.go import GO, GOJSONViewModel
from biota.sbo import SBO
from biota.chebi_ontology import chebi_ontology
from biota.taxonomy import Taxonomy
from biota.bto import BTO

#import external module 
from rhea.rhea import Rhea
from brenda.brenda import brenda
from onto.ontology import Onto
from chebi.chebi import Chebi
from taxonomy.taxo import Taxo

############################################################################################
#
#                                        class main_admin
#                                         
############################################################################################
test_data_path = settings.get_data("biota_test_data_dir")

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

class TestMain(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        GO.drop_table()
        GOJSONViewModel.drop_table()
        GO.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        #GO.drop_table()
        pass
    
    def test_db_object(self):
        ### Test GO class ###
        files = dict(
            go_data = "./go/go.obo",
            sbo_data = "./sbo/sbo.obo",
            chebi_data = "./chebi/chebi.obo",
            bto_json_data = "./brenda/bto/bto.json",
            brenda_file = "brenda_download_20200504.txt",
            chebi_compound_file = "./chebi/flat_files/compounds.tsv",
            chebi_chemical_data_file = "./chebi/flat_files/chemical_data.tsv",
            rhea_kegg_reaction_file = './rhea/tsv/rhea-kegg.reaction',
            rhea_direction_file = './rhea/tsv/rhea-directions.tsv',
            rhea2ecocyc_file = './rhea/tsv/rhea2ecocyc.tsv',
            rhea2metacyc_file = './rhea/tsv/rhea2metacyc.tsv',
            rhea2macie_file = './rhea/tsv/rhea2macie.tsv',
            rhea2kegg_reaction_file = './rhea/tsv/rhea2kegg_reaction.tsv',
            rhea2ec_file = './rhea/tsv/rhea2ec.tsv'
        )

        GO.create_go(test_data_path, **files)
        self.assertEqual(GO.get(GO.go_id == 'GO:0000001').name, "mitochondrion inheritance")
        go1 = GO.get(GO.go_id == 'GO:0000001')
        go1_view_model = GOJSONViewModel(go1)
        GOJSONViewModel.save_all()
        view = go1_view_model.render()
        self.assertEqual(view, '{"id": GO:0000001 , "name": mitochondrion inheritance, "namespace": biological_process , "definition": The distribution of mitochondria, including the mitochondrial genome, into daughter cells after mitosis or meiosis, mediated by interactions between mitochondria and the cytoskeleton. }')
