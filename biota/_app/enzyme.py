from biota.controller import Controller
from fastapi.requests import Request

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

@staticmethod
# URL: ./page/biota/enzyme/stats
async def enzyme_stats(request: Request):
    return Controller.fetch_enzyme_stats()


@staticmethod
# URL: ./page/biota/enzo/
async def enzo_entity(request: Request):
    uri = request.query_params.get('uri')
    return Controller.fetch_entity(uri, model_type="enzyme")

@staticmethod
# URL: ./page/biota/enzo/[index]
async def enzo_index(request: Request):
    return await Page.enzyme_list(request)

@staticmethod
# URL: ./page/biota/enzo/list
async def enzo_list(request: Request):
    page = request.query_params.get('page',1)
    return Controller.fetch_enzyme_list(page=page)

@staticmethod
# URL: ./page/biota/enzo/stats
async def enzo_stats(request: Request):
    return Controller.fetch_enzyme_stats()