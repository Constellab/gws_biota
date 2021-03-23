# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import asyncio
import click
from gws.settings import Settings
from gws.logger import Info, Warning, Error

from biota._cli.db_creator import DbCreator
from gws.model import Protocol, Experiment, Study

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--user', default="Gencoverer", help='User name')
@click.option('--no-fts', is_flag=True, help='Activate Fulltext Search')
def createdb(ctx, user="Gencoverer", no_fts=False):
    settings = Settings.retrieve()
    settings.activate_fts(not no_fts)
    settings.save()

    Info(f"Hello {user}")
    Info(f"Creating tables ...")

    params = dict(
        go_file         = "./go/go.obo",
        sbo_file        = "./sbo/sbo.obo",
        eco_file        = "./eco/eco.obo",
        chebi_file      = "./chebi/obo/chebi.obo",
        bto_file        = "./brenda/bto/bto.json",
        pwo_file        = "./pwo/pwo.obo",
        brenda_file     = "./brenda/brenda/brenda_download.txt",
        protein_file    = "./uniprot/uniprot_sprot.fasta",
        bkms_file       = "./bkms/Reactions_BKMS.csv",
        ncbi_node_file          = "./ncbi/taxdump/nodes.dmp",
        ncbi_name_file          = "./ncbi/taxdump/names.dmp",
        ncbi_division_file      = "./ncbi/taxdump/division.dmp",
        ncbi_citation_file      = "./ncbi/taxdump/citations.dmp",
    
        expasy_enzclass_file    = "./expasy/enzclass.txt",
        
        rhea_reaction_file      = './rhea/rhea-reactions.txt',
        rhea_direction_file     = './rhea/tsv/rhea-directions.tsv',
        rhea2ecocyc_file        = './rhea/tsv/rhea2ecocyc.tsv',
        rhea2metacyc_file       = './rhea/tsv/rhea2metacyc.tsv',
        rhea2macie_file         = './rhea/tsv/rhea2macie.tsv',
        rhea2kegg_reaction_file = './rhea/tsv/rhea2kegg_reaction.tsv',
        rhea2ec_file            = './rhea/tsv/rhea2ec.tsv',
        rhea2reactome_file      = './rhea/tsv/rhea2reactome.tsv',
        
        reactome_pathways_file          = './reactome/ReactomePathways.txt',
        reactome_pathway_relations_file = './reactome/ReactomePathwaysRelation.txt',
        reactome_chebi_pathways_file    = './reactome/ChEBI2Reactome.txt'
    )

    dirs = settings.get_data("dirs")
    for k in dirs:
        if k.startswith("biota:"):
            params[k] = dirs[k]

    db_creator = DbCreator()
    
    protocol = Protocol(
        name = 'biota_db_creation',
        processes = { 'db_creator': db_creator },
        connectors = [],
        interfaces = {},
        outerfaces = {}
    )
    
    for k in params:
        db_creator.set_param(k, params[k])
    
    #create a defaut study
    study = Study.get_default_instance()
    e = protocol.create_experiment(study=study)
    asyncio.run( e.run() )