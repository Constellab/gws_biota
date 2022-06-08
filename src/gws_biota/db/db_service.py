# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (BadRequestException, BaseService, CurrentUserService,
                      Experiment, ExperimentService, Job, Logger, ModelService,
                      MySQLBase, MySQLService, Protocol, Queue, QueueService,
                      Requests, Settings, TaskModel, TaskService, UserService)
from gws_core.extra import BaseModelService

from ..biomass_reaction.biomass_reaction import BiomassReaction
from ..bto.bto import BTO
from ..compound.compound import Compound
from ..eco.eco import ECO, ECOAncestor
from ..enzyme.deprecated_enzyme import DeprecatedEnzyme
from ..enzyme.enzyme import Enzyme, EnzymeOrtholog
from ..enzyme.enzyme_class import EnzymeClass
from ..enzyme.enzyme_pathway import EnzymePathway
from ..go.go import GO
from ..ontology.ontology import Ontology
from ..organism.organism import Organism
from ..pathway.pathway import Pathway
from ..protein.protein import Protein
from ..reaction.reaction import Reaction
from ..sbo.sbo import SBO
from ..taxonomy.taxonomy import Taxonomy
from .db_creator import DbCreator, DbCreatorHelper
from .db_manager import DbManager


class DbService(BaseService):

    @classmethod
    def build_biota_db(cls, user=None) -> Experiment:
        """
        Build biota db
        """

        cls.create_tables()
        DbCreatorHelper.run()
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
