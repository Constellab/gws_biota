# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import Optional
from pydantic import BaseModel
from fastapi.requests import Request

from gws.query import Query, Paginator
from gws.model import Controller, Experiment

from biota.controller import Controller

class Page:

    @staticmethod
    # URL: ./page/biota/
    async def index(request: Request):
        return await Page.dashboard(request)

    @staticmethod
    # URL: ./page/biota/dashboard
    async def dashboard(request: Request):
        try:
            return { "status": True, "data": {} }
        except Exception as err:
            return {"status": False, "data": f"{err}"}

    @staticmethod
    # URL: ./page/biota/bto
    async def bto(request: Request):
        page = request.query_params.get('page',1)
        try:
            data = Controller.fetch_bto_list(page=page)
            return { "status": True, "data": data }
        except Exception as err:
            return {"status": False, "data": f"{err}"}

    @staticmethod
    # URL: ./page/biota/eco
    async def eco(request: Request):
        page = request.query_params.get('page',1)
        try:
            data = Controller.fetch_eco_list(page=page)
            return { "status": True, "data": data }
        except Exception as err:
            return {"status": False, "data": f"{err}"}

    @staticmethod
    # URL: ./page/biota/sbo
    async def sbo(request: Request):
        page = request.query_params.get('page',1)
        try:
            data = Controller.fetch_sbo_list(page=page)
            return { "status": True, "data": data }
        except Exception as err:
            return {"status": False, "data": f"{err}"}

    @staticmethod
    # URL: ./page/biota/pwo
    async def pwo(request: Request):
        page = request.query_params.get('page',1)
        try:
            data = Controller.fetch_pwo_list(page=page)
            return { "status": True, "data": data }
        except Exception as err:
            return {"status": False, "data": f"{err}"}

    @staticmethod
    # URL: ./page/biota/taxonomy
    async def taxonomy(request: Request):
        page = request.query_params.get('page',1)
        try:
            data = Controller.fetch_taxonomy_list(page=page)
            return { "status": True, "data": data }
        except Exception as err:
            return {"status": False, "data": f"{err}"}

class API:
    pass