# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import click

from gws.settings import Settings
from gws.logger import Logger
from biota.db.backend import DbCreator
from gws.model import Protocol

def createdb(user):
    if user is None:
        user = "Gencoverer"

    logger = Logger()
    logger.info(f"Hello {user}")
    logger.info(f"Creating tables ...")

    settings = Settings.retrieve()

    params = dict(
        go_file = "go.obo",
        sbo_file = "sbo.obo",
        eco_file = "eco.obo",
        chebi_file = "./obo/chebi.obo",
        bto_file = "bto.json",
        pwo_file = "./pwo/pwo.obo",
        brenda_file = "./brenda/brenda_download.txt",
        fasta_file = "./uniprot/uniprot_sprot.fasta",
        bkms_file = "./bkms/Reactions_BKMS.csv",
        #chebi_compound_file = "./tsv/compounds.tsv",
        #chebi_chemical_data_file = "./tsv/chemical_data.tsv",
        #chebi_sdf_file = "./sdf/ChEBI_complete.sdf",
        ncbi_node_file = "./taxdump/nodes.dmp",
        ncbi_name_file = "./taxdump/names.dmp",
        ncbi_division_file = "./taxdump/division.dmp",
        ncbi_citation_file = "./taxdump/citations.dmp",
        rhea_kegg_reaction_file = './kegg/rhea-kegg.reaction',
        rhea_direction_file = './tsv/rhea-directions.tsv',
        rhea2ecocyc_file = './tsv/rhea2ecocyc.tsv',
        rhea2metacyc_file = './tsv/rhea2metacyc.tsv',
        rhea2macie_file = './tsv/rhea2macie.tsv',
        rhea2kegg_reaction_file = './tsv/rhea2kegg_reaction.tsv',
        rhea2ec_file = './tsv/rhea2ec.tsv',
        rhea2reactome_file = './tsv/rhea2reactome.tsv'
    )

    dirs = settings.get_data("dirs")
    for k in dirs:
        if k.startswith("biota:"):
            params[k] = dirs[k]

    db_creator = DbCreator()
    for k in params:
        db_creator.set_param(k, params[k])

    protocol = Protocol(
        name = 'biota_db_creation',
        processes = { 'db_creator': db_creator },
        connectors = [],
        interfaces = {},
        outerfaces = {}
    )

    import asyncio
    asyncio.run( protocol.run() )