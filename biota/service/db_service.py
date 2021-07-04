# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws.settings import Settings
from gws.logger import Info, Warning, Error
from gws.model import Protocol, Experiment, Study
from gws.service import BaseService
from gws.http import HTTPInternalServerError
from gws.queue import Queue, Job
from gws.requests import Requests

from biota.proc.db import DbCreator
from biota.base import Base

class DbService(BaseService):

    @classmethod
    def build_biota_db(cls, user=None, clean: bool=True) -> Experiment:
        """
        Build biota db
        """

        from gws.user_service import UserService

        if clean:
            cls.clean_biota_db()

        db_creator = DbCreator()
        study = Study.get_default_instance()
        user = UserService.get_current_user()
        e = db_creator.create_experiment(study=study, user=user)
        e.set_title("Creation of biota database")

        try:
            q = Queue()
            job = Job(user=user, experiment=e)
            q.add(job, auto_start=True)
            return e
        except Exception as err:
            raise HTTPInternalServerError(detail=f"An error occured.", debug_error=err) from err


