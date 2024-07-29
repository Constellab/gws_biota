# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (ConfigParams, OutputSpec, OutputSpecs, Task, TaskInputs, Settings,
                      TaskOutputs, task_decorator, Folder, StrParam)

from Bio import Entrez
from ..extract_data.pubmed import Pubmed
from ..extract_data.geoprofiles import GeoProfiles
from ..extract_data.gene import Gene
from ..extract_data.clinvar import ClinVar
from ..extract_data.protein import Protein
from ..extract_data.gds import GDS
from ..extract_data.popset import PopSet


@task_decorator("RequestNCBI", human_name="Request NCBI",
                short_description="Send a request to the NCBI")
class RequestNCBI(Task):
    output_specs = OutputSpecs({'results': OutputSpec(Folder, human_name="Results",
                               short_description="Folders containing the results")})

    config_specs = {
        "query": StrParam(
            human_name="Query", short_description="The user query"),
        "choice_DB": StrParam(
            default_value="PubMed", human_name="Database",
            short_description="Select the database of interest",
            allowed_values=["PubMed", "Gene", "GDS", "Popset", "GeoProfiles", "Protein", "ClinVar"])}

# --------------------- RUN ---------------------
    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        # Retrieve the query for the request
        query: str = params["query"]

        database: str = params["choice_DB"]

        uids = Entrez.read(Entrez.esearch(db=database, term=query, retmax=10000))

        # Destination directory where files will be downloaded
        destination_dir: str = Settings.make_temp_dir()

        folder: Folder
        if database == "GeoProfiles":
            folder = GeoProfiles.get_geoprofiles_data(destination_dir, uids)
        elif database == "PubMed":
            folder = Pubmed.get_all_pubmed_articles(destination_dir, uids)
        elif database == "Gene":
            folder = Gene.get_gene_data(destination_dir, uids)
        elif database == "ClinVar":
            folder = ClinVar.get_clinvar_data(destination_dir, uids)
        elif database == "Protein":
            folder = Protein.get_protein_data(destination_dir, uids)
        elif database == "GDS":
            folder = GDS.get_geodataset(destination_dir, uids)
        elif database == "Popset":
            folder = PopSet.get_popset_data(destination_dir, uids)
        else:
            self.log_error_message("This request is not NCBI compliant")
        return {'results': folder}


# TODO :
# - changer les print par des log.message
# - si le fichier est déjà téléchargé, continue
# - lever des exceptions
# - ajout de messages si la query ne retourne rien
