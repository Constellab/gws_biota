# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

# from ..base.base_ft import BaseFT

# @typing_registrator(unique_name="Compartment", object_type="MODEL", hide=True)
# class Compartment(BaseFT):
#     go_id = CharField(null=True, index=True)
#     bigg_id = CharField(null=True, index=True)

import json
import os

from gws_core import BadRequestException

__cdir__ = os.path.dirname(os.path.abspath(__file__))


class CompartmentNotFoundException(BadRequestException):
    """ CompartmentNotFoundException """


class Compartment:
    """ Comaprtment """

    go_id = None
    bigg_id = None
    name = None
    data = None

    _db_data: dict = None

    def __init__(self, *, go_id="", bigg_id="", name="", data=None):
        self.go_id = go_id
        self.bigg_id = bigg_id
        self.name = name
        self.data = data or {}

    @classmethod
    def search_by_name(cls, name: str):
        """ Search by name """
        comparts = []
        db_data = cls._get_db_data()
        for val in db_data:
            if (name in val["name"]) or (name in val["data"]["synonymes"].join(",")):
                comparts.append(Compartment(**val))
        return comparts

    @classmethod
    def get_by_go_id(cls, go_id: str):
        """ Get by GO id """
        db_data = cls._get_db_data()
        for val in db_data:
            if val["go_id"] == go_id:
                return Compartment(**val)
        raise CompartmentNotFoundException("Compartment not found")

    @classmethod
    def get_by_bigg_id(cls, bigg_id: str):
        """ Get by GO id """
        db_data = cls._get_db_data()
        for val in db_data:
            if val["bigg_id"] == bigg_id:
                return Compartment(**val)
        raise CompartmentNotFoundException("Compartment not found")

    @classmethod
    def _get_db_data(cls):
        if cls._db_data is None:
            with open(os.path.join(__cdir__, "./data/compartment.json"), 'r', encoding="utf-8") as fp:
                cls._db_data = json.load(fp)
        return cls._db_data["data"]
