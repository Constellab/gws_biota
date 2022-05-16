# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import random
from typing import Dict, List, TypedDict, Union

from gws_core import Logger

GRID_SCALE = 10
GRID_INTERVAL = 10

CompoundClusterDict = TypedDict("CompoundClusterDict", {
    "name": List[dict],
    "x": str,
    "y": str,
    "level": int
})

CompoundLayoutDict = TypedDict("CompoundLayoutDict", {
    "x": str,
    "y": str,
    "clusters": List[dict],
})


class CompoundCluster:
    """ CompoundCluster """

    _name: str = None
    _data: Dict[str, Dict] = None
    _centroid: dict = None

    def __init__(self, name, data: Dict, centroid: Dict = None):
        if not isinstance(data, dict):
            raise Exception("The data must be a dict")
        self._name = name
        self._data = data
        if centroid is None:
            self._centroid = {"x": 0, "y": 0}
        else:
            self._centroid = centroid

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    @property
    def centroid(self):
        return self._centroid

    def set_position(self, centroid):
        """ Set centroid """
        self._centroid = centroid

    def generate(self):
        """ Generate positions """
        data = {}
        for c_id, c_data in self._data.items():
            c_data["x"] = GRID_SCALE * (c_data["x"] + self._centroid["x"])
            c_data["y"] = - GRID_SCALE * (c_data["y"] + self._centroid["y"])
            c_data["cluster"] = self._name
            data[c_id] = c_data
        return data

    @ staticmethod
    def from_file(file_path) -> 'CompoundCluster':
        """ Create a CompoundCluster using a JSON data file """
        with open(file_path, "r", encoding="utf-8") as fp:
            try:
                cdata = json.load(fp)
                return CompoundCluster(name=cdata["name"], data=cdata["data"], centroid=cdata.get("centroid"))
            except Exception as err:
                raise Exception(f'Cannot load JSON file "{file_path}"') from err


class CompoundLayout:
    """ CompoundLayout """

    _clusters: List[CompoundCluster] = []

    __data: dict = {}
    __flat_data: dict = {}

    __is_flattened = False
    __is_generated = False

    @ classmethod
    def add_cluster(cls, cluster):
        """ Add cluster """
        if not isinstance(cluster, CompoundCluster):
            raise Exception("The cluster must be CompoundCluster")
        cls._clusters.append(cluster)

    @ classmethod
    def generate(cls, db_path: str = None, force: bool = False):
        """ Generate positions """

        if not force and cls.__is_generated:
            return cls.__data

        if not db_path:
            db_path = os.path.join("./_layout/", os.path.dirname(os.path.abspath(__file__)))

        data = {}
        try:
            # loads for all .json files
            for root, _, files in os.walk(db_path):
                for file in files:
                    if file.endswith(".json"):
                        cluster = CompoundCluster.from_file(os.path.join(root, file))
                        cls._clusters.append(cluster)

            for cluster in cls._clusters:
                data.update(cluster.generate())
        except Exception as err:
            Logger.warning(f"An error occur when parsing layout files. Message {err}")

        cls.__is_generated = True
        cls.__data = data
        return data

    @classmethod
    def get_flat_data(cls, force: bool = False):
        """ Get layout data """
        if not force and cls.__is_flattened:
            return cls.__flat_data

        cls.__flat_data = {}
        data = CompoundLayout.generate()
        for key, val in data.items():
            if key not in cls.__flat_data:
                cls.__flat_data[key] = {}

            cluster_name = val["cluster"]
            pos = {
                "name": cluster_name,
                "x": val["x"],
                "y": val["y"],
                "level": val.get("level", 2),
            }
            cls.__flat_data[key][cluster_name] = pos
            for alt_key in val.get("alt", []):
                if alt_key not in cls.__flat_data:
                    cls.__flat_data[alt_key] = {}

                cls.__flat_data[alt_key][cluster_name] = pos

        cls.__is_flattened = True
        return cls.__flat_data

    @classmethod
    def get_layout_by_chebi_id(cls, synonym_chebi_ids: Union[str, List[str]], compartment=None) -> CompoundLayoutDict:
        """ Get layout position matching with the CheBI id """

        position = {"x": None, "y": None, "clusters": {}}
        if not synonym_chebi_ids:
            return position

        def rnd_offset():
            rnd_num = random.uniform(0, 1)
            return GRID_INTERVAL if rnd_num >= 0.5 else -GRID_INTERVAL

        clusters: List[CompoundClusterDict] = {}

        if isinstance(synonym_chebi_ids, str):
            clusters = cls.get_flat_data().get(synonym_chebi_ids, {})
        else:
            # look up and take the first one
            for chebi_id in synonym_chebi_ids:
                clusters = cls.get_flat_data().get(chebi_id, {})
                if clusters:
                    break

        if not clusters:
            return position

        default_position: CompoundLayoutDict = list(clusters.values())[0]
        position: CompoundLayoutDict = {
            "x": default_position["x"],
            "y": default_position["y"],
            "clusters": clusters,
        }

        # add offset for compartment
        if compartment and compartment != "c":
            position["x"] += rnd_offset() * GRID_SCALE
            position["y"] += rnd_offset() * GRID_SCALE

        return position
