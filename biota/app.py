# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https:/gencovery.com

from typing import Optional
from pydantic import BaseModel
from fastapi.requests import Request

from gws.query import Query, Paginator
from gws.model import Controller, Experiment

from biota.controller import Controller

class Page:

    # -- B -- 

    @staticmethod
    # URL: ./page/biota/bto/[index]
    async def bto_index(request: Request):
        return await Page.bto_list(request)

    @staticmethod
    # URL: ./page/biota/bto/entity
    async def bto_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="bto")

    @staticmethod
    # URL: ./page/biota/bto/list
    async def bto_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_bto_list(page=page)

    # -- C --

    @staticmethod
    # URL: ./page/biota/compound/[index]
    async def compound_index(request: Request):
        return await Page.compound_list(request)

    @staticmethod
    # URL: ./page/biota/compound/list
    async def compound_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_compound_list(page=page)

    @staticmethod
    # URL: ./page/biota/compound/entity
    async def compound_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="compound")

    # -- E -- 
    
    @staticmethod
    # URL: ./page/biota/eco/[index]
    async def eco_index(request: Request):
        return await Page.eco_list(request)

    @staticmethod
    # URL: ./page/biota/eco/list
    async def eco_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_eco_list(page=page)

    @staticmethod
    # URL: ./page/biota/eco/entity
    async def eco_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="eco")

    # -- E --
    
    @staticmethod
    # URL: ./page/biota/eco/enzyme
    async def enzyme_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="enzyme")

    @staticmethod
    # URL: ./page/biota/enzyme/[index]
    async def enzyme_index(request: Request):
        return await Page.enzyme_list(request)

    @staticmethod
    # URL: ./page/biota/enzyme/list
    async def enzyme_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_enzyme_list(page=page)

    # -- I --

    @staticmethod
    # URL: ./page/biota/[[index]/[index]]
    async def index_index(request: Request):
        return await Page.index_dashboard(request)

    @staticmethod
    # URL: ./page/biota/[index/dashboard]
    async def index_dashboard(request: Request):
        return Controller.fetch_last_stats()

    # -- R --

    @staticmethod
    # URL: ./page/biota/reaction/[index]
    async def reaction_index(request: Request):
        return await Page.reaction_list(request)

    @staticmethod
    # URL: ./page/biota/reaction/list
    async def reaction_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_reaction_list(page=page)

    @staticmethod
    # URL: ./page/biota/reaction/entity
    async def reaction_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="reaction")

    # -- S --

    @staticmethod
    # URL: ./page/biota/sbo/[index]
    async def sbo_index(request: Request):
        return await Page.sbo_list(request)

    @staticmethod
    # URL: ./page/biota/sbo/list
    async def sbo_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_sbo_list(page=page)

    @staticmethod
    # URL: ./page/biota/sbo/entity
    async def sbo_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="sbo")

    @staticmethod
    # URL: ./page/biota/stats/last
    async def stats_last(request: Request):
        return Controller.fetch_last_stats()

    # -- T --

    @staticmethod
    # URL: ./page/biota/taxonomy/[index]
    async def taxonomy_index(request: Request):
        return await Page.taxonomy_list(request)

    @staticmethod
    # URL: ./page/biota/taxonomy/list
    async def taxonomy_list(request: Request):
        page = request.query_params.get('page',1)
        return Controller.fetch_taxonomy_list(page=page)
    
    @staticmethod
    # URL: ./page/biota/taxonomy/entity
    async def taxonomy_entity(request: Request):
        uri = request.query_params.get('uri')
        return Controller.fetch_entity(uri, model_type="taxonomy")


class API:
    pass