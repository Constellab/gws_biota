# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https:/gencovery.com

from fastapi import Request

from gws.queue import Queue, Job
from gws.http import *
from .service.db_service import create_experiment as create_db_experiment

class API:

    # -- C --

    async def build_db() -> dict:
        """
        Build biota db
        """
        
        from .service.db_service import DbService

        e = DbService.build_biota_db()           
        return e.to_json()

    # -- D --

    async def dump_db( data: dict ) -> dict:
        """
        Dump biota db
        """

        from gws.service.mysql_service import MySQLService

        MySQLService.dump_db("biota")           
        return True
    
    # -- L --

    async def load_db( data: dict ) -> dict:
        """
        Load biota db
        """

        from gws.service.mysql_service import MySQLService

        MySQLService.load_db("biota", remote_file_url=data["url"])           
        return True
