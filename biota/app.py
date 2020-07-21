from gws.settings import Settings
from gws.prism.app import App as BaseApp
from starlette.routing import Route, Mount
from starlette.endpoints import HTTPEndpoint
from starlette.templating import Jinja2Templates

####################################################################################
#
# HTTP and WebSocket endpoints
#
####################################################################################

settings = Settings.retrieve()
template_dir = settings.get_template_dir("biota")
templates = Jinja2Templates(directory=template_dir)

async def homepage(request):
    return templates.TemplateResponse('home.html', {'request': request, 'settings': settings})

class App(BaseApp):

    @classmethod
    def on_init(cls):

        #biota routes
        cls.routes.append(Route('/biota/home/', homepage) )