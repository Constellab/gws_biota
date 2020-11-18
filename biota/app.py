# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import Optional
from pydantic import BaseModel

from gws.query import Query
from biota.db.bto import BTO
 

NUMBER_OF_ITEMS_PER_PAGE = 20

class _ApiModel(BaseModel):
    page: Optional[int] = 1
    filter: Optional[str] = ""


class Page:

    @staticmethod
    # URL: ./page/biota/
    # Params: [GET=q, POST=data]
    async def index(request, q=None, data=None):
        return None


class API:

    @staticmethod
    # URL: ./page/biota/bto-list
    async def bto_list(request):
        page = request.query_params.get('page',1)
        Q = BTO.select().paginate(page, NUMBER_OF_ITEMS_PER_PAGE)
        return Query.select_query_to_list(Q, return_format="json")