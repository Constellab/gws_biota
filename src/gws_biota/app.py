# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https:/gencovery.com

from fastapi import Request

from gws_core import MySQLService, Queue, Job
from .service.db_service import DbService

class API:

    # -- C --

    @staticmethod
    async def build_db() -> dict:
        """
        Build biota db
        """
    
        e = DbService.build_biota_db()           
        return e.to_json()

    # -- D --

    @staticmethod
    async def dump_db( data: dict ) -> dict:
        """
        Dump biota db
        """
        MySQLService.dump_db("biota")           
        return True
    
    # -- L --

    @staticmethod
    async def load_db( data: dict ) -> dict:
        """
        Load biota db
        """

        MySQLService.load_db("biota", remote_file_url=data["url"])           
        return True
