# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os

from gws.settings import Settings
from gws.protocol import Protocol
from gws.experiment import Experiment
from gws.study import Study
from gws.service.base_service import BaseService
from gws.queue import Queue, Job
from gws.requests import Requests

from gws.exception.bad_request_exception import BadRequestException

from ..proc.db_creator import DbCreator
from ..base import Base

class DbService(BaseService):

    @classmethod
    def build_biota_db(cls, user=None) -> Experiment:
        """
        Build biota db
        """

        from gws.service.user_service import UserService

        db_creator = DbCreator()
        study = Study.get_default_instance()
        if not user:
            user = UserService.get_current_user()
        e = db_creator.create_experiment(study=study, user=user)
        e.set_title("Creation of biota database")
        try:
            q = Queue()
            job = Job(user=user, experiment=e)
            q.add(job, auto_start=True)
            return e
        except Exception as err:
            raise BadRequestException(f"An error occured while adding the experiment to the job queue") from err
    
    @classmethod
    def dump_biota_db(cls) -> bool:
        from gws.service.mysql_service import MySQLService
        MySQLService.dump_db("biota", force=True, wait=False)
        return True

    @classmethod
    def is_busy(cls) -> bool:
        from gws.service.mysql_service import MySQLService
        from gws.db.mysql import MySQLBase
        base = MySQLBase()
        base.set_default_config("biota")
        return not base.is_ready()

    @classmethod
    def is_ready(cls) -> bool:
        from gws.service.mysql_service import MySQLService
        from gws.db.mysql import MySQLBase
        base = MySQLBase()
        base.set_default_config("biota")
        return base.is_ready()

    @classmethod
    def load_biota_db(cls) -> bool:
        from gws.service.mysql_service import MySQLService
        MySQLService.load_db("biota", force=True, wait=True)
        return True