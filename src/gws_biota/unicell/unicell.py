# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import hashlib
import pickle
from typing import Dict, List

import networkx as nx
import numpy
from gws_biota import Compound
from gws_core import BadRequestException
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import BigBitField, BlobField, CharField
from scipy import sparse
from scipy.sparse import linalg

from ..base.base_ft import BaseFT


@typing_registrator(unique_name="Unicell", object_type="MODEL", hide=True)
class Unicell(BaseFT):
    """
    The unicell
    """

    compound_id_list = BlobField()
    reaction_id_list = BlobField()
    compound_x_list = BlobField()
    compound_y_list = BlobField()
    rhea_edge_map = BlobField()
    graph = BlobField()

    _compound_x_list: List[float] = None
    _compound_y_list: List[float] = None
    _compound_id_list: List[str] = None
    _reaction_id_list: List[str] = None
    _rhea_edge_map: Dict[str, List[str]] = None
    _graph = None

    _table_name = 'biota_unicell'

    @classmethod
    def retrieve(cls):
        """ Retrieve the unicell """
        try:
            return Unicell.get_by_id(0)
        except:
            from .unicell_service import UnicellService
            return UnicellService.create_unicell()

    def _create_hash_object(self):
        """ DEACTIVATE HASH """
        hash_obj = hashlib.blake2b()
        return hash_obj

    @property
    def nb_compounds(self):
        """ Returns the number of compounds  """
        return len(self.get_compound_id_list())

    @property
    def nb_reactions(self):
        """ Returns the number of reactions  """
        return len(self.get_reaction_id_list())

    def get_compound_id_list(self):
        """ Get compound_id_list matrix """
        if self._compound_id_list is None:
            self._compound_id_list = pickle.loads(self.compound_id_list)
        return self._compound_id_list

    def get_reaction_id_list(self):
        """ Get reaction_id_list matrix """
        if self._reaction_id_list is None:
            self._reaction_id_list = pickle.loads(self.reaction_id_list)
        return self._reaction_id_list

    def get_rhea_edge_map(self) -> Dict[str, List[str]]:
        """ Get rhea_edge mapping dictionnary """
        if self._rhea_edge_map is None:
            self._rhea_edge_map = pickle.loads(self.rhea_edge_map)
        return self._rhea_edge_map

    def get_subgraph(self, rhea_id_list: List[str]):
        " Get subgraph "
        edges = []
        rhea_edge_map = self.get_rhea_edge_map()
        for rhea_id in rhea_id_list:
            val = rhea_edge_map[rhea_id]
            edges.extend(val)
        return self.get_graph().edge_subgraph(edges)

    def get_graph(self):
        """ Get graph """
        if self._graph is None:
            self._graph = pickle.loads(self.graph)
        return self._graph

    def get_compound_id_at(self, i) -> int:
        """ Get index of a compound using its chebi_id """
        comp_list = self.get_compound_id_list()
        return comp_list[i]

    def get_index_of_compound_id(self, chebi_id) -> str:
        """ Get chebi_id at a given index """
        comp_list = self.get_compound_id_list()
        if chebi_id in comp_list:
            return comp_list.index(chebi_id)
        else:
            raise BadRequestException(f"The chebi id {chebi_id} is not found")

    def get_reaction_id_at(self, i) -> str:
        """ Get rhea_id at a given index """
        rxn_list = self.get_reaction_id_list()
        return rxn_list[i]

    def get_index_of_reaction_id(self, rhea_id) -> int:
        """ Get index of a reaction using its rhea_id """
        rxn_list = self.get_reaction_id_list()
        if rhea_id in rxn_list:
            return rxn_list.index(rhea_id)
        else:
            raise BadRequestException(f"The rhea id {rhea_id} is not found")

    def get_edge(self, chebi_id1, chebi_id2):
        """ Get an edge """
        return self.get_graph().edges[chebi_id1, chebi_id2]

    def get_all_edges(self):
        """ Get an edge """
        return self.get_graph().edges

    def are_connected(self, chebi_id1, chebi_id2) -> bool:
        """ Check if two compounds are connected """
        graph = self.get_graph()
        return nx.has_path(graph, chebi_id1, chebi_id2)

    def shortest_path(self, chebi_id1, chebi_id2) -> list:
        """ Get the shortest path between components """
        graph = self.get_graph()
        return nx.shortest_path(graph, chebi_id1, chebi_id2)
