# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import random
from typing import Dict, List, TypedDict, Union

from gws_core import BadRequestException, Logger

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
    _parent: str = None
    _data: Dict[str, Dict] = None
    _centroid: dict = None
    _level: int = 2

    def __init__(self, parent, name, data: Dict, centroid: Dict = None):
        if not isinstance(data, dict):
            raise BadRequestException("The data must be a dict")
        self._name = name
        self._parent = parent
        self._data = data
        if not centroid:
            self._centroid = {"x": 0, "y": 0}
        else:
            self._centroid = centroid

        if not isinstance(self._centroid["x"], (float, int)):
            self._centroid["x"] = 0
        if not isinstance(self._centroid["y"], (float, int)):
            self._centroid["y"] = 0

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
        for comp_id, comp_data in self._data.items():
            comp_data["x"] = GRID_SCALE * (comp_data["x"] + self._centroid["x"])
            comp_data["y"] = - GRID_SCALE * (comp_data["y"] + self._centroid["y"])
            comp_data["parent"] = self._parent
            comp_data["name"] = self._name
            data[comp_id] = comp_data
        return data

    @ staticmethod
    def from_file(file_path) -> 'CompoundCluster':
        """ Create a CompoundCluster using a JSON data file """
        with open(file_path, "r", encoding="utf-8") as fp:
            try:
                cdata = json.load(fp)
            except Exception as err:
                raise BadRequestException(f'Cannot load JSON file "{file_path}"') from err

            folder = (file_path.split("/"))[-2]
            return CompoundCluster(
                parent=cdata.get("parent", folder),
                name=cdata["name"],
                data=cdata["data"],
                centroid=cdata.get("centroid"))


class CompoundLayout:
    """ CompoundLayout """

    X_LIMIT = 2000
    Y_LIMIT = 4000

    _clusters: List[CompoundCluster] = []

    _data: dict = {}
    _flat_data: dict = {}
    _is_flattened = False
    _is_generated = False

    @ classmethod
    def add_cluster(cls, cluster):
        """ Add cluster """
        if not isinstance(cluster, CompoundCluster):
            raise BadRequestException("The cluster must be CompoundCluster")
        cls._clusters.append(cluster)

    @ classmethod
    def generate(cls, db_path: str = None, force: bool = False):
        """ Generate positions """

        if cls._is_generated:
            if not force:
                return cls._data

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
        except Exception as err:
            Logger.warning(f"An error occur when parsing layout files. Message {err}")

        for cluster in cls._clusters:
            cluster_data = cluster.generate()
            for comp_id in cluster_data:
                if comp_id not in data:
                    data[comp_id] = {}
                cluster_name = cluster_data[comp_id]["name"]
                data[comp_id][cluster_name] = cluster_data[comp_id]

        cls._is_generated = True
        cls._data = data
        return data

    @classmethod
    def get_flat_data(cls, force: bool = False):
        """ Get layout data """
        if cls._is_flattened:
            if not force:
                return cls._flat_data

        cls._flat_data = {}
        data = CompoundLayout.generate()
        for comp_id, cluster_data in data.items():
            cls._flat_data[comp_id] = cluster_data
            # parse current cluster and gather all comp data
            for current_cluster_data in cluster_data.values():
                #current_cluster_data = cluster_name[cluster_name]
                for alt_comp_id in current_cluster_data.get("alt", []):
                    cls._flat_data[alt_comp_id] = cluster_data

            # cluster_data
        cls._is_flattened = True
        return cls._flat_data

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
            "level": default_position.get("level", 2),
            "clusters": clusters,
        }

        # add offset for compartment
        if compartment and compartment != "c":
            position["x"] += rnd_offset() * GRID_SCALE
            position["y"] += rnd_offset() * GRID_SCALE

        if position["x"] > cls.X_LIMIT or position["x"] < -cls.X_LIMIT:
            position["x"] = None
            position["y"] = None

        if position["y"]:
            if position["y"] > cls.Y_LIMIT or position["y"] < -cls.Y_LIMIT:
                position["x"] = None
                position["y"] = None

        return position
