import json
import os
from typing import List, Optional

from gws_core import BadRequestException, BaseModelDTO

__cdir__ = os.path.dirname(os.path.abspath(__file__))


class Compartments():
    all_compartments: List['Compartment'] = None


class CompartmentNotFoundException(BadRequestException):
    """ CompartmentNotFoundException """


class Compartment(BaseModelDTO):
    """ Compartment """

    go_id: str = None
    bigg_id: str = None
    name: str = None
    color: Optional[str] = None
    alt_go_ids: List[str] = []
    synonymes: List[str] = []
    is_steady: bool = False

    def has_name_or_synonym(self, name: str) -> bool:
        """ Check if has name or synonym """
        return name == self.name or (name in self.synonymes)

    @classmethod
    def get_steady_compartments(cls) -> List['Compartment']:
        """ Get steady compartments """
        return [compartment for compartment in cls.get_all_compartments() if compartment.is_steady]

    @classmethod
    def search_by_name(cls, name: str) -> List['Compartment']:
        """ Search by name """
        comparts: List[Compartment] = []
        for compartment in cls.get_all_compartments():
            if compartment.has_name_or_synonym(name):
                comparts.append(compartment)
        return comparts

    @classmethod
    def get_by_go_id_or_none(cls, go_id: str) -> Optional['Compartment']:
        """ Get by GO id """
        for compartment in cls.get_all_compartments():
            if compartment.go_id == go_id:
                return compartment
        return None

    @classmethod
    def get_by_go_id(cls, go_id: str) -> Optional['Compartment']:
        """ Get by GO id and raise exception if not found"""
        compartment = cls.get_by_go_id_or_none(go_id)
        if compartment:
            return compartment
        raise CompartmentNotFoundException(f"Compartment with go_id '{go_id}' not found")

    @classmethod
    def get_by_bigg_id_or_none(cls, bigg_id: str) -> Optional['Compartment']:
        """ Get by BiGG id """
        for compartment in cls.get_all_compartments():
            if compartment.bigg_id == bigg_id:
                return compartment
        return None

    @classmethod
    def get_by_bigg_id(cls, bigg_id: str) -> 'Compartment':
        """ Get by BiGG id and raise exception if not found"""
        compartment = cls.get_by_bigg_id_or_none(bigg_id)
        if compartment:
            return compartment
        raise CompartmentNotFoundException(f"Compartment with bigg_id '{bigg_id}' not found")

    @classmethod
    def get_by_big_id_or_go_id_or_none(cls, id_: str) -> Optional['Compartment']:
        """ Get by BiGG id or GO id """
        compartment = cls.get_by_bigg_id_or_none(id_)
        if compartment:
            return compartment
        compartment = cls.get_by_go_id_or_none(id_)
        if compartment:
            return compartment
        return None

    @classmethod
    def get_by_big_id_or_go_id(cls, id_: str) -> 'Compartment':
        """ Get by BiGG id or GO id and raise exception if not found"""
        compartment = cls.get_by_big_id_or_go_id_or_none(id_)
        if compartment:
            return compartment
        raise CompartmentNotFoundException(f"Compartment with id '{id_}' not found")

    @classmethod
    def get_all_compartments(cls) -> List['Compartment']:
        if Compartments.all_compartments is None:
            with open(os.path.join(__cdir__, "./data/compartment.json"), 'r', encoding="utf-8") as fp:
                compartments = json.load(fp)
                Compartments.all_compartments = Compartment.from_json_list(compartments.get("data"))

        return Compartments.all_compartments
