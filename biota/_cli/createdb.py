# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import click
from gws.settings import Settings
from gws.logger import Logger
from biota.db.backend import DbCreator
from gws.model import Protocol, Experiment

def createdb(user):
    if user is None:
        user = "Gencoverer"

    Logger.info(f"Hello {user}")
    Logger.info(f"Creating tables ...")

    settings = Settings.retrieve()

    params = dict(
        go_file         = "./go/go.obo",
        sbo_file        = "./sbo/sbo.obo",
        eco_file        = "./eco/eco.obo",
        chebi_file      = "./chebi/obo/chebi.obo",
        bto_file        = "./brenda/bto/bto.json",
        pwo_file        = "./pwo/pwo.obo",
        brenda_file     = "./brenda/brenda/brenda_download.txt",
        fasta_file      = "./uniprot/uniprot_sprot.fasta",
        bkms_file       = "./bkms/Reactions_BKMS.csv",
        ncbi_node_file          = "./ncbi/taxdump/nodes.dmp",
        ncbi_name_file          = "./ncbi/taxdump/names.dmp",
        ncbi_division_file      = "./ncbi/taxdump/division.dmp",
        ncbi_citation_file      = "./ncbi/taxdump/citations.dmp",
        rhea_kegg_reaction_file = './rhea/kegg/rhea-kegg.reaction',
        rhea_direction_file     = './rhea/tsv/rhea-directions.tsv',
        rhea2ecocyc_file        = './rhea/tsv/rhea2ecocyc.tsv',
        rhea2metacyc_file       = './rhea/tsv/rhea2metacyc.tsv',
        rhea2macie_file         = './rhea/tsv/rhea2macie.tsv',
        rhea2kegg_reaction_file = './rhea/tsv/rhea2kegg_reaction.tsv',
        rhea2ec_file            = './rhea/tsv/rhea2ec.tsv',
        rhea2reactome_file      = './rhea/tsv/rhea2reactome.tsv'
    )

    dirs = settings.get_data("dirs")
    for k in dirs:
        if k.startswith("biota:"):
            params[k] = dirs[k]

    db_creator = DbCreator()
    for k in params:
        db_creator.set_param(k, params[k])

    e = Experiment()
    protocol = Protocol(
        name = 'biota_db_creation',
        processes = { 'db_creator': db_creator },
        connectors = [],
        interfaces = {},
        outerfaces = {}
    )
    protocol.set_active_experiment(e)

    import asyncio
    asyncio.run( protocol.run() )