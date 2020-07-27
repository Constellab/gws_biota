# GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws.settings import Settings
from gws.prism.controller import Controller
from gws.app import App as GWSApp
from starlette.routing import Route, Mount
from starlette.endpoints import HTTPEndpoint
from starlette.templating import Jinja2Templates

from biota.prism.go import GO, GOJSONStandardViewModel, GOJSONPremiumViewModel
from biota.prism.taxonomy import Taxonomy, TaxonomyJSONStandardViewModel, TaxonomyJSONPremiumViewModel
from biota.prism.compound import Compound, CompoundJSONStandardViewModel, CompoundJSONPremiumViewModel
#from biota.prism.enzyme import Enzyme, EnzymeJSONStandardViewModel, EnzymeJSONPremiumViewModel, EnzymeStatistics, EnzymeStatisticsProcess

import json
####################################################################################
#
# HTTP and WebSocket endpoints
#
####################################################################################

settings = Settings.retrieve()
template_dir = settings.get_template_dir("biota")
templates = Jinja2Templates(directory=template_dir)
go_size = GO.select().count()

dict_descriptions = {
    "GO": "The Gene Ontology: a major bioinformatics initiative to unify the representation of gene and gene product attributes across all species."
}

async def homepage(request):
    return templates.TemplateResponse('home.html', {'request': request, 'settings': settings})

async def tablepage(request):
    return templates.TemplateResponse('tables.html', {'request': request, 'settings': settings})

async def test_view(request):
    #view = App.get_go_example_views()
    dict_ = App.get_go_example_views()
    for view in dict_.keys():
        dict_[view] = json.loads(dict_[view])

    response = templates.TemplateResponse('test_view.html', {'request': request, 'settings': settings, "views": dict_})
    return response
    #return (templates.TemplateResponse('test_view.html', {'request': request, 'settings': settings}))
    #return templates.TemplateResponse('test_view.html', {'request': request, 'settings': settings})

class App(GWSApp):

    @classmethod
    def on_init(cls):
        super().on_init()

        #biota routes
        cls.routes.append(Route('/biota/home/', homepage) )
        cls.routes.append(Route('/biota/tables/', tablepage) )
        cls.routes.append(Route('/biota/testviews/', test_view ) )
    
    def get_go_example_views():
        dict_views = {}
        list_views = []
        # ------------------ First example ------------------ #
        go1 = GO.get(GO.go_id == 'GO:0000006')
        go1_premium_view_model = GOJSONStandardViewModel(go1)
        view1 = go1_premium_view_model.render()
        list_views.append(view1)

        # ------------------ Second example ------------------ #
        go2 = GO.get(GO.go_id == 'GO:0000011')
        go2_premium_view_model = GOJSONPremiumViewModel(go2)
        view2 = go2_premium_view_model.render()
        list_views.append(view2)

        # ------------------ Third example ------------------ #
        go3 = GO.get(GO.go_id == 'GO:0000012')
        go3_premium_view_model = GOJSONPremiumViewModel(go3)
        view3 = go3_premium_view_model.render()
        dict_views = {1: view1.replace('\'', '\"'), 2: view2.replace("\'", ""), 3: view3.replace("\'", "")}
        list_views.append(view1)

        return dict_views


