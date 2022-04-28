# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import Dict, List


class Cluster:
    """ Cluster """

    _data: Dict[str, Dict] = None
    _position: dict = None

    def __init__(self, compound_data: Dict, position=None):
        if not isinstance(compound_data, dict):
            raise Exception("The data must be a dict")
        self._data = compound_data
        if position is None:
            self._position = {"x": 0, "y": 0}
        else:
            self._position = position

    def set_position(self, position):
        """ Set position """
        self._position = position

    def generate(self):
        """ Generate positions """
        data = {}
        for c_id, c_data in self._data.items():
            c_data["x"] += self._position["x"]
            c_data["y"] += self._position["y"]
            data[c_id] = c_data
        return data


class Layout:
    """ Layout """

    _clusters: List[Cluster] = []

    @ classmethod
    def add_cluster(cls, cluster):
        """ Add cluster """
        if not isinstance(cluster, Cluster):
            raise Exception("The cluster must be Cluster")
        cls._clusters.append(cluster)

    @ classmethod
    def generate(cls):
        """ Generate positions """
        data = {}
        for c in cls._clusters:
            data.update(c.generate())
        return data
