# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (BadRequestException, BaseService, CurrentUserService,
                      Experiment, ExperimentService, Job, MySQLBase,
                      MySQLService, Protocol, Queue, QueueService, Requests,
                      Settings, TaskModel, TaskService, UserService, Logger, ModelService)
from gws_core.extra import BaseModelService

from .db_creator import DbCreator, DbCreatorHelper
from .db_manager import DbManager

from ..biomass_reaction.biomass_reaction import BiomassReaction
from ..bto.bto import BTO
from ..compound.compound import Compound
from ..eco.eco import ECO,ECOAncestor
from ..enzyme.enzyme import Enzyme, EnzymeOrtholog
from ..enzyme.deprecated_enzyme import DeprecatedEnzyme
from ..enzyme.enzyme_class import EnzymeClass
from ..enzyme.enzyme_pathway import EnzymePathway
from ..reaction.reaction import Reaction
from ..go.go import GO
from ..sbo.sbo import SBO
from ..organism.organism import Organism
from ..protein.protein import Protein
from ..taxonomy.taxonomy import Taxonomy
from ..pathway.pathway import Pathway
from ..ontology.ontology import Ontology

class DbService(BaseService):

    @classmethod
    def build_biota_db(cls, user=None) -> Experiment:
        """
        Build biota db
        """

        cls.create_tables()
        DbCreatorHelper.run()
        
        cls_list = [ 
            BTO, BiomassReaction, Compound, ECO, 
            DeprecatedEnzyme, EnzymeClass, EnzymeOrtholog, 
            EnzymePathway, Enzyme, GO, Ontology, Organism, Pathway, 
            Protein, Reaction, SBO, Taxonomy
        ]
        for c in cls_list:
            Logger.info(f"Creating {c.__name__} ft index ...")
            c.create_full_text_index()
        Logger.info("Done")

    @classmethod
    def create_tables(cls):
        """
        Create tables
        """

        DbManager.init(mode="dev")
        DbManager._DEACTIVATE_PROTECTION_ = True

        if ECO.table_exists():
            BaseModelService.drop_tables()

        if ECO.table_exists():
            if ECO.select().count():
                raise BadRequestException("A none empty biota database already exists")

        BaseModelService.drop_tables()
        BaseModelService.create_tables()
        ModelService.register_all_processes_and_resources()

        if not ECO.table_exists():
            raise BadRequestException("Cannot create tables")

        if not ECOAncestor.table_exists():
            raise BadRequestException("Cannot create ancestor tables")