# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import sys
import os
import unittest
import copy
import asyncio
import click
import logging

#import from gws
from gws.prism.controller import Controller

#import from biota
from gws.settings import Settings
from biota.db.go import GO
from biota.db.sbo import SBO
from biota.db.bto import BTO
from biota.db.eco import ECO
from biota.db.chebi_ontology import ChebiOntology
from biota.db.taxonomy import Taxonomy
from biota.db.compound import Compound
from biota.db.enzyme_function import EnzymeFunction
from biota.db.enzyme_annotation import EnzymeAnnotation
from biota.db.reaction import Reaction

#import Timer
from timeit import default_timer
import time

settings = Settings.retrieve()
data_paths = settings.get_data("biota:biodata_dir")

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--user', '-n', help='User name')
def createdb(ctx, user):

    __cdir__ = os.path.dirname(os.path.abspath(__file__))
    fh = logging.FileHandler(os.path.join(__cdir__,'./biota.log'))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(" %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # drop tables
    GO.drop_table()
    SBO.drop_table()
    BTO.drop_table()
    ECO.drop_table()
    ChebiOntology.drop_table()
    Taxonomy.drop_table()
    Compound.drop_table()
    EnzymeFunction.drop_table()
    Reaction.drop_table()
    EnzymeAnnotation.drop_table()

    # create tables
    GO.create_table()
    SBO.create_table()
    BTO.create_table()
    ECO.create_table()
    ChebiOntology.create_table()
    Taxonomy.create_table()
    Compound.create_table()
    EnzymeFunction.create_table()
    Reaction.create_table()
    EnzymeAnnotation.create_table()
    
    if user is None:
        user = "Gencoverer"
    
    
    logger.info(f"Hello {user}")
    logger.info("Start creating biota_db...")

    files = dict(
            go_data = "go.obo",
            sbo_data = "sbo.obo",
            eco_data = "eco.obo",
            chebi_data = "./obo/chebi.obo",
            bto_json_data = "bto.json",
            brenda_file = "./brenda/brenda_download.txt",
            chebi_compound_file = "./tsv/compounds.tsv",
            chebi_chemical_data_file = "./tsv/chemical_data.tsv",
            ncbi_nodes = "./taxdump/nodes.dmp",
            ncbi_names = "./taxdump/names.dmp",
            ncbi_division = "./taxdump/division.dmp",
            ncbi_citations = "./taxdump/citations.dmp",
            rhea_kegg_reaction_file = './kegg/rhea-kegg.reaction',
            rhea_direction_file = './tsv/rhea-directions.tsv',
            rhea2ecocyc_file = './tsv/rhea2ecocyc.tsv',
            rhea2metacyc_file = './tsv/rhea2metacyc.tsv',
            rhea2macie_file = './tsv/rhea2macie.tsv',
            rhea2kegg_reaction_file = './tsv/rhea2kegg_reaction.tsv',
            rhea2ec_file = './tsv/rhea2ec.tsv',
            rhea2reactome_file = './tsv/rhea2reactome.tsv'
        )

    # ------------- Create GO ------------- #
    logger.info("Step 1 | Loading go and go_ancestors...")
    start_time = time.time()
    biota:go_biodata_dir = settings.get_data("biota:go_biodata_dir")
    GO.create_go_db(biota:go_biodata_dir, **files)
    len_go = GO.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #go = {}".format(elapsed_time/60, len_go))
    
    # ------------- Create SBO ------------- #
    logger.info("Step 2 | Loading sbo and sbo_ancestors...")
    start_time = time.time()
    biota:sbo_biodata_dir = settings.get_data("biota:sbo_biodata_dir")
    SBO.create_sbo_db(biota:sbo_biodata_dir, **files)
    len_sbo = SBO.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} sec for #sbo= {}".format(elapsed_time, len_sbo))
    
    # ------------------- Create BTO ----------------- #
    logger.info("Step 3 | Loading bto and bto_ancestors...")
    start_time = time.time()
    biota:bto_biodata_dir = settings.get_data("biota:bto_biodata_dir")
    BTO.create_bto_db(biota:bto_biodata_dir, **files)
    len_bto = BTO.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} sec for #bto = {}".format(elapsed_time, len_bto))
    
    # ------------------- Create ECO ----------------- #
    logger.info("Step 4 | Loading eco and eco_ancestors...")
    start_time = time.time()
    biota:eco_biodata_dir = settings.get_data("biota:eco_biodata_dir")
    ECO.create_eco_db(biota:eco_biodata_dir, **files)
    len_eco = ECO.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} sec for #eco = {}".format(elapsed_time, len_eco))
    
    # ------------- Create ChebiOntology ------------- #
    logger.info("Step 5 | Loading chebi ontology...")
    start_time = time.time()
    biota:chebi_biodata_dir = settings.get_data("biota:chebi_biodata_dir")
    ChebiOntology.create_chebi_ontology_db(biota:chebi_biodata_dir, **files)
    len_chebi_ontology = ChebiOntology.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #chebi_ontology = {}".format(elapsed_time/60, len_chebi_ontology))

    # ---------------- Create Taxonomy --------------- #
    logger.info("Step 6 | Loading ncbi taxonomy...")
    start_time = time.time()
    ncbi_biodata_dir = settings.get_data("biota:taxonomy_biodata_dir")
    Taxonomy.create_taxonomy_db(ncbi_biodata_dir, **files)
    len_taxonomy = Taxonomy.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #taxa = {}".format(elapsed_time/60, len_taxonomy))
    
    # ---------------- Create Compound --------------- #
    logger.info("Step 7 | Loading chebi compounds...")
    start_time = time.time()
    biota:chebi_biodata_dir = settings.get_data("biota:chebi_biodata_dir")
    Compound.create_compound_db(biota:chebi_biodata_dir, **files)
    len_compound = Compound.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #compounds = {} ".format(elapsed_time/60, len_compound))

    # ------------------ Create EnzymeFunction --------------- #
    logger.info("Step 8 | Loading brenda enzyme_functions and enzyme_btos...")
    start_time = time.time()
    biota:brenda_biodata_dir = settings.get_data("biota:brenda_biodata_dir")
    EnzymeFunction.create_enzyme_function_db(biota:brenda_biodata_dir, **files)
    len_enzyme = EnzymeFunction.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #enzyme_functions = {} ".format(elapsed_time/60, len_enzyme))
    
    # ---------------- Create Reactions -------------- #
    logger.info("Step 9 | Loading rhea reactions...")
    start_time = time.time()
    biota:rhea_biodata_dir = settings.get_data("biota:rhea_biodata_dir")
    Reaction.create_reaction_db(biota:rhea_biodata_dir, **files)
    len_rhea = Reaction.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #rhea = {}".format(elapsed_time/60, len_rhea))
    
    """"
    # ------------- Create EnzymeAnnotation ------------- #
    logger.info("Step 10 | Loading enzyme_function annotations...")
    start_time = time.time()
    EnzymeAnnotation.create_annotation_db()
    len_enzyme_annotation = EnzymeAnnotation.select().count()
    elapsed_time = time.time() - start_time
    logger.info("... done in {:10.2f} min for #enzyme_annotations = {}".format(elapsed_time/60, len_enzyme_annotation))
    """