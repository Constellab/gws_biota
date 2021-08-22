# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os

from gws_core import (Settings, Protocol, Experiment, Study, Queue, Job, Requests, 
                        BaseService, MySQLBase, MySQLService, BadRequestException,
                        Experiment, ExperimentService)
from gws_core import UserService, CurrentUserService, QueueService

from ..proc.db_creator import DbCreator
from ..base import Base

class DbService(BaseService):

    @classmethod
    def build_biota_db(cls, user=None) -> Experiment:
        """
        Build biota db
        """

        db_creator = DbCreator()
        study = Study.get_default_instance()
        if not user:
            #user = CurrentUserService.get_current_user()
            user = UserService.get_sysuser()
            user.is_http_authenticated = True
            user.is_console_authenticated = True
            user.save()
            CurrentUserService.set_current_user(user)

        
        experiment: Experiment =  ExperimentService.create_experiment_from_process(process=db_creator)
        experiment.save()
        experiment.set_title("Creation of biota database")
        try:
            q = Queue()
            job = Job(user=user, experiment=experiment)
            QueueService.add_job(job, auto_start=True)
            return experiment
        except Exception as err:
            raise BadRequestException(f"An error occured while adding the experiment to the job queue") from err
    
    @classmethod
    def dump_biota_db(cls) -> bool:
        MySQLService.dump_db("biota", force=True, wait=False)
        return True

    @classmethod
    def is_busy(cls) -> bool:
        base = MySQLBase()
        base.set_default_config("biota")
        return not base.is_ready()

    @classmethod
    def is_ready(cls) -> bool:
        base = MySQLBase()
        base.set_default_config("biota")
        return base.is_ready()

    @classmethod
    def load_biota_db(cls) -> bool:
        MySQLService.load_db("biota", force=True, wait=True)
        return True