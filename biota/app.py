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
template_dir = settings.get_template_dir("biota")
templates = Jinja2Templates(directory=template_dir)

async def homepage(request):
    return templates.TemplateResponse('home.html', {'request': request, 'settings': settings})

async def tablepage(request):
    return templates.TemplateResponse('tables.html', {'request': request, 'settings': settings})

async def cardpage(request):
    return templates.TemplateResponse('card.html', {'request': request, 'settings': settings})

async def test_view(request):
    return templates.TemplateResponse('test_view.html', {'request': request, 'settings': settings})

class App:
    """
    App class of biota application

    This App class will dynamically inherits the App classes this application depends on.
    Method on_init() must be overloaded to add new routes.
    """

    routes = []

    @classmethod
    def on_init(cls):
        """
        Initializes the application. 
        
        This method is automatically called after by the constructor.
        """
        # loads base applications' routes
        super().on_init()

        # adds new routes
        cls.routes.append(Route('/biota/home/', homepage) )
        cls.routes.append(Route('/biota/tables/', tablepage) )
        cls.routes.append(Route('/biota/card/{name}/{id}', cardpage) )
        cls.routes.append(Route('/biota/testviews/', test_view ) )

