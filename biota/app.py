# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json

from starlette.routing import Route, Mount
from starlette.endpoints import HTTPEndpoint
from starlette.templating import Jinja2Templates

from gws.settings import Settings
from gws.prism.controller import Controller

settings = Settings.retrieve()
template_dir = settings.get_public_dir("biota")
templates = Jinja2Templates(directory=template_dir)

async def homepage(request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "settings": settings
    })

class App:
    """
    App class of Biota.
    """

    routes = []

    @classmethod
    def init_routes(cls):
        """
        Defines the web routes of the brick.

        Routing coventions: 
        
        To prevent route collisions, it is highly recommended to 
        prefix route names of the name of the current brick.
        e.g.: 
            * /<brick name>/home/       -> home page route
            * /<brick name>/settings/   -> setting page route
        """

        # adds new routes
        cls.routes.append(Route('/biota/', homepage) )

