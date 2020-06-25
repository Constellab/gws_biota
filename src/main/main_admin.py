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
from biota.go import GO
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
input_db_dir = settings.get_data("biota_db_path")

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

Controller.reset(GO)
GO.create_go(input_db_dir, **files)
Controller.register_models([GO])
Controller.save_all()
