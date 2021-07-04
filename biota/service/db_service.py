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
    def create_biota_db(cls, user=None) -> Experiment:
        from gws.user_service import UserService

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

    # -- D --

    @classmethod
    def dump_biota_db(cls, url):
        from gws.mysql import MySQLDump
        dest_dir = "/data/backup/mariadb/biota/"

        load = MySQLDump()
        load.user="biota"
        load.password="gencovery"
        load.db_name="biota"
        load.table_prefix="biota_"
        load.output_dir=dest_dir
        load.host="biota_prod_db"
        load.run()

    # -- L --

    @classmethod
    def load_biota_db(cls, url):
        from gws.mysql import MySQLLoad
        dest_dir = "/data/backup/mariadb/biota/"

        Requests.download(url, dest_dir=dest_dir)

        load = MySQLLoad()
        load.user="biota"
        load.password="gencovery"
        load.db_name="biota"
        load.table_prefix="biota_"
        load.output_dir=dest_dir
        load.host="biota_prod_db"
        load.run()

    # -- R --

    @classmethod
    def remove_biota_db(cls):
        from gws.model import ModelService
        ModelService.drop_tables(instance_type=Base)
        ModelService.create_tables(instance_type=Base)
    

