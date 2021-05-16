# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https:/gencovery.com

from biota._admin.createdb import create_experiment as create_db_experiment
from gws.http import *
from fastapi import Request
from gws.queue import Queue, Job

class API:

    async def create_db( data: dict ) -> dict:
        """
        Create biota db

        :param request: The request
        :type request: `fastapi.Request`
        :return: The json response
        :rtype: `dict`
        """
        
        from gws.service.user_service import UserService
        user = UserService.get_current_user()
        fts = data.get("fts", True)
        e = create_db_experiment(user, fts=fts)
        
        job = Job(user=user, experiment=e)
        Queue.add(job, auto_start=True)            
        return e.to_json()