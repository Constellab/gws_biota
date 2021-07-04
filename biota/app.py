# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https:/gencovery.com

from biota.service.db_service import create_experiment as create_db_experiment
from gws.http import *
from fastapi import Request
from gws.queue import Queue, Job

class API:

    # -- C --

    async def create_db() -> dict:
        """
        Create biota db
        """
        
        from biota.service.db_service import DbService

        e = DbService.create_biota_db()           
        return e.to_json()

    # -- D --

    async def dump_db( data: dict ) -> dict:
        """
        Dump biota db
        """

        from biota.service.db_service import DbService

        DbService.dump_biota_db()           
        return True
    
    # -- L --

    async def load_db( data: dict ) -> dict:
        """
        Load biota db
        """

        from biota.service.db_service import DbService

        DbService.load_biota_db(url=data["url"])           
        return True

    # -- R --

    async def remove_db( data: dict ) -> dict:
        """
        Drop biota db
        """

        from biota.service.db_service import DbService

        DbService.remove_biota_db()           
        return True