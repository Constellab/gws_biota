# Core GWS app module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import Optional
from pydantic import BaseModel
from fastapi.requests import Request

from gws.query import Query, Paginator
from gws.controller import Controller as BaseController
from biota.db.bto import BTO
from biota.db.eco import ECO
from biota.db.pwo import PWO
from biota.db.sbo import SBO
from biota.db.taxonomy import Taxonomy
from biota.db.enzyme import Enzyme
from biota.db.reaction import Reaction
from biota.db.compound import Compound

class Controller(BaseController):

    @classmethod
    def fetch_bto_list(cls, page=1, name=""):            
        Q = BTO.select() #.order_by(BTO.bto_id.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_eco_list(cls, page=1, name=""):            
        Q = ECO.select() #.order_by(ECO.eco_id.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_pwo_list(cls, page=1, name=""):            
        Q = PWO.select() #.order_by(PWO.pwo_id.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_sbo_list(cls, page=1, name=""):            
        Q = SBO.select() #.order_by(SBO.sbo_id.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_taxonomy_list(cls, page=1, name=""):            
        Q = Taxonomy.select() #.order_by(Taxonomy.tax_id.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_enzyme_list(cls, page=1, name=""):            
        Q = Enzyme.select() #.order_by(Enzyme.ec_number.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_reaction_list(cls, page=1, name=""):            
        Q = Reaction.select().where(Reaction.direction == 'UN') #.order_by(Reaction.ec_number.desc())
        return Paginator(Q, page=page).as_model_list()

    @classmethod
    def fetch_compound_list(cls, page=1, name=""):            
        Q = Compound.select().where(Compound.mass > 0) #.order_by(Reaction.ec_number.desc())
        return Paginator(Q, page=page).as_model_list()