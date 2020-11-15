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

# Pages

async def index_page(request, q=None, data=None):
    return None



async def bto_list_api(request, q=None, data=None):
    params: BaseModel = Query.parse(q, Model=_ApiModel)
    params = params.dict()

    page = 1
    if page in params:
        page = params[page]

    print(page)

    Q = BTO.select().paginate(page, NUMBER_OF_ITEMS_PER_PAGE)

    print(len(Q))
    
    return Query.select_query_to_list(Q, return_format="json")