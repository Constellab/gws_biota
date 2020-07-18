import sys
import os
import unittest
import copy
import asyncio
import click

#import from gws
from gws.prism.controller import Controller

#import from biota
from gws.settings import Settings
from biota.go import GO
from biota.sbo import SBO
from biota.bto import BTO
from biota.eco import ECO
from biota.chebi_ontology import ChebiOntology
from biota.taxonomy import Taxonomy
from biota.compound import Compound
from biota.enzyme import Enzyme
from biota.enzyme_annotation import EnzymeAnnotation
from biota.reaction import Reaction

#import external module 
from rhea.rhea import Rhea
from brenda.brenda import Brenda
from onto.ontology import Onto
from chebi.chebi import Chebi
from taxo.taxonomy import Taxo

#import Timer
from timeit import default_timer
import time

############################################################################################
#
#                                        class CLI (Command Line Interface)
#                                         
############################################################################################
settings = Settings.retrieve()
data_paths = settings.get_data("biota_db_data_dir")

enzyme_bto = Enzyme.bto.get_through_model()

# files_model = dict(
#     substrate_reaction = Reaction.substrates.get_through_model(),
#     product_reaction = Reaction.products.get_through_model(),
#     enzyme_reaction = Reaction.enzymes.get_through_model()
#     )

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))

@click.pass_context
@click.option('--name', '-n', help='Output path')

def createdb(ctx, name):
    # --- drops --- #
    GO.drop_table()
    SBO.drop_table()
    BTO.drop_table()
    ECO.drop_table()
    ChebiOntology.drop_table()
    Taxonomy.drop_table()
    Compound.drop_table()
    Enzyme.drop_table()
    enzyme_bto.drop_table()
    #Reaction.drop_table(**files_model)
    Reaction.drop_table()
    EnzymeAnnotation.drop_table()

    # --- creations --- #
    GO.create_table()
    SBO.create_table()
    BTO.create_table()
    ECO.create_table()
    ChebiOntology.create_table()
    Taxonomy.create_table()
    Compound.create_table()
    Enzyme.create_table()
    enzyme_bto.create_table()
    #Reaction.create_table(**files_model)
    Reaction.create_table()
    EnzymeAnnotation.create_table()
    
    print("Hello", name)
    print("Start loading biota_db...")

    files = dict(
            go_data = "go.obo",
            sbo_data = "sbo.obo",
            eco_data = "eco.obo",
            chebi_data = "chebi.obo",
            bto_json_data = "bto.json",
            brenda_file = "brenda_download.txt",
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file = "chemical_data.tsv",
            ncbi_nodes = "nodes.dmp",
            ncbi_names = "names.dmp",
            ncbi_division = "division.dmp",
            ncbi_citations = "citations.dmp",
            rhea_kegg_reaction_file = 'rhea-kegg.reaction',
            rhea_direction_file = 'rhea-directions.tsv',
            rhea2ecocyc_file = 'rhea2ecocyc.tsv',
            rhea2metacyc_file = 'rhea2metacyc.tsv',
            rhea2macie_file = 'rhea2macie.tsv',
            rhea2kegg_reaction_file = 'rhea2kegg_reaction.tsv',
            rhea2ec_file = 'rhea2ec.tsv',
            rhea2reactome_file = 'rhea2reactome.tsv'
        )

    # ------------- Create GO ------------- #
    start_time = time.time()

    go_input_db_dir = data_paths["go"]
    GO.create_go(go_input_db_dir, **files)
    len_go = len(GO.select())
    
    elapsed_time = time.time() - start_time
    print("step 1 | Loading go and go_ancestors in: time = {} min for #go = {}".format(elapsed_time/60, len_go))
    
    
    # ------------- Create SBO ------------- #
    start_time = time.time()

    sbo_input_db_dir = data_paths["sbo"]
    SBO.create_sbo(sbo_input_db_dir, **files)
    len_sbo = len(SBO.select())

    elapsed_time = time.time() - start_time
    print("step 2 | Loading sbo and sbo_ancestors in: time = {} sec for #sbo= {}".format(elapsed_time, len_sbo))
    
    
    # ------------- Create BTO ------------- #
    start_time = time.time()

    bto_input_db_dir = data_paths["bto"]
    BTO.create_bto(bto_input_db_dir, **files)
    len_bto = len(BTO.select())

    elapsed_time = time.time() - start_time
    print("step 3 | Loading bto and bto_ancestors in: time = {} sec for #bto = {}".format(elapsed_time, len_bto))
    
    # ------------- Create ECO ------------- #
    start_time = time.time()

    eco_input_db_dir = data_paths["eco"]
    ECO.create_eco(eco_input_db_dir, **files)
    len_eco = len(ECO.select())
    
    elapsed_time = time.time() - start_time
    print("step 4 | Loading eco and eco_ancestors in: time = {} sec for #eco = {}".format(elapsed_time, len_eco))
    
    # ------------- Create ChebiOntology ------------- #
    start_time = time.time()

    chebi_input_db_dir = data_paths["chebi"]
    ChebiOntology.create_chebi(chebi_input_db_dir, **files)
    len_chebi_ontology = len(ChebiOntology.select())
    
    elapsed_time = time.time() - start_time
    print("step 5 | Loading chebi ontology in: time = {} min for #chebi_ontology = {}".format(elapsed_time/60, len_chebi_ontology))
    
    # ------------- Create Taxonomy ------------- #
    start_time = time.time()

    ncbi_input_db_dir = data_paths["ncbi"]
    Taxonomy.create_taxons(ncbi_input_db_dir, bulk_size = 750, **files)
    len_taxonomy = len(Taxonomy.select())
    
    elapsed_time = time.time() - start_time
    print("step 6 | Loading taxonomy in: time = {} for #taxons = {}".format(elapsed_time/60, len_taxonomy))
    
    # ------------- Create Compound ------------- #
    start_time = time.time()

    chebi_input_db_dir = data_paths["chebi"]
    Compound.create_compounds_from_files(chebi_input_db_dir, **files)
    len_compound = Compound.select()
    
    elapsed_time = time.time() - start_time
    print("step 7 | Loading compounds in: time = {} for #compounds = {} ".format(elapsed_time/60, len_compound))

    # ------------- Create Enzyme ------------- #
    start_time = time.time()

    brenda_texfile_input_db_dir = data_paths["brenda"]
    Enzyme.create_enzymes_from_dict(brenda_texfile_input_db_dir, **files)
    len_enzyme = Enzyme.select()
    
    elapsed_time = time.time() - start_time
    print("step 8 | Loading enzymes and enzymes_btos in: time = {} for #enzymes = {} ".format(elapsed_time/60, len_enzyme))
    
    # ------------- Create Reactions ------------- #
    start_time = time.time()

    rhea_input_db_dir = data_paths["rhea"]
    Reaction.create_reactions_from_files(rhea_input_db_dir, **files)
    len_rhea = Reaction.select()

    elapsed_time = time.time() - start_time
    print("step 9 | Loading reactions, reactions_enzymes, reactions_substrates, reactions_products in: time = {} for #rhea = {}".format(elapsed_time/60, len_rhea))
    
    """
    # ------------- Create EnzymeAnnotation ------------- #
    start_time = time.time()

    EnzymeAnnotation.create_annotation()
    
    elapsed_time = time.time() - start_time
    print("step 7 | Loading enzymes_annotations: time = {}".format(elapsed_time/60))
    """