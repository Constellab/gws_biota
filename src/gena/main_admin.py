import sys
import os
import unittest
import copy
import asyncio

#import from gws
from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Resource
from gws.prism.controller import Controller
from gws.prism.controller import Controller

#import from pewee
from peewee import CharField, ForeignKeyField, chunked
from peewee import CharField, ForeignKeyField, chunked

#import from starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

#import from gena
from manage import settings
from gena.compound import Compound
from gena.reaction import Reaction
from gena.enzyme import Enzyme
from gena.go import GO
from gena.sbo import SBO
from gena.chebi_ontology import chebi_ontology
from gena.taxonomy import Taxonomy
from gena.bto import BTO

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


input_db_dir = settings.get_data("gena_db_path")
substrate_reaction = Reaction.substrates.get_through_model()
product_reaction = Reaction.products.get_through_model()
enzyme_reaction = Reaction.enzymes.get_through_model()