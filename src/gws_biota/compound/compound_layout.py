# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import copy
import json
import os
import random
from typing import Dict, List, TypedDict, Union

from gws_core import BadRequestException, Logger, StringHelper

GRID_SCALE = 3
GRID_INTERVAL = 100

GOLBAL_CENTER = {"x": 719, "y": 513}  # center on pyruvate

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

SHIFTS = {
    "xenobiotic_biodegradation": {"x": -300, "y": 0},
    "energy_metabolism": {"x": -200, "y": 0},
    "lipid_metabolism": {"x": -200, "y": 0},
    "carbohydrate_metabolism": {"x": 0, "y": 0},
    "glycan_metabolism": {"x": 20, "y": 0},
    "amino_acid_metabolism": {"x": 100, "y": 0},
    "nucleotide_metabolism": {"x": 100, "y": 0},
    "vitamin_and_cofactor_metabolism": {"x": 300, "y": 0},
    "other_secondary_metabolite_metabolism": {"x": 400, "y": 0},
    "terpenoid_and_polyketide_metabolism": {"x": 400, "y": 0},
    "urea_cycle": {"x": 200, "y": 0}
}


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
        self._centroid = {"x": 0, "y": 0}
        if centroid:
            self._centroid = centroid
            if isinstance(self._centroid["x"], (float, int)):
                self._centroid["x"] -= GOLBAL_CENTER["x"] - SHIFTS[parent]["x"]
            else:
                self._centroid["x"] = 0
            if isinstance(self._centroid["y"], (float, int)):
                self._centroid["y"] -= GOLBAL_CENTER["y"] - SHIFTS[parent]["y"]
            else:
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
            if comp_data["x"] is not None:
                comp_data["x"] = GRID_SCALE * (comp_data["x"] + self._centroid["x"])
            if comp_data["y"] is not None:
                comp_data["y"] = GRID_SCALE * (comp_data["y"] + self._centroid["y"])
            comp_data["parent"] = self._parent
            comp_data["name"] = self._name
            # comp_data["master_id"] = comp_id
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
                parent=StringHelper.slugify(cdata.get("parent", folder), snakefy=True),
                name=cdata["name"],
                data=cdata["data"],
                centroid=cdata.get("centroid"))


class CompoundLayout:
    """ CompoundLayout """

    X_LIMIT = 4000
    Y_LIMIT = 4000
    GRID_SCALE = GRID_SCALE
    GRID_INTERVAL = GRID_INTERVAL
    BIOMASS_CLUSTER_CENTER = {"x": 1000, "y": 200}

    _clusters: List[CompoundCluster] = []

    _data: dict = {}
    _flat_data: dict = {}
    _is_flattened = False
    _is_generated = False
    _master_ids_map = {}

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
            raise BadRequestException(f"An error occur when parsing layout files. Message {err}") from err

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
            cls._master_ids_map[comp_id] = comp_id

            # parse current cluster and gather all comp data
            for current_cluster_data in cluster_data.values():
                # current_cluster_data = cluster_name[cluster_name]
                for alt_comp_id in current_cluster_data.get("alt", []):
                    cls._flat_data[alt_comp_id] = cluster_data
                    cls._master_ids_map[alt_comp_id] = comp_id

            # cluster_data
        cls._is_flattened = True
        return cls._flat_data

    @classmethod
    def get_layout_by_chebi_id(cls, synonym_chebi_ids: Union[str, List[str]]) -> CompoundLayoutDict:
        """ Get layout position matching with the CheBI id """

        position = {"x": None, "y": None, "clusters": {}}
        if not synonym_chebi_ids:
            return position

        def rnd_offset():
            """ Random offset """
            rnd_num = random.uniform(0, 1)
            return GRID_SCALE * (GRID_INTERVAL if rnd_num >= 0.5 else -GRID_INTERVAL)

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
            "x": None,
            "y": None,
            "level": default_position.get("level", 2),
            "clusters": clusters,
        }

        for c_name in position["clusters"]:
            position["clusters"][c_name]["alt"] = None

        return position

    @classmethod
    def get_biomass_position(cls):
        """ Formats and returns biomass position """
        return {
            "x": None,  # cls.BIOMASS_CLUSTER_CENTER["x"] * cls.GRID_SCALE,
            "y": None,  # cls.BIOMASS_CLUSTER_CENTER["y"] * cls.GRID_SCALE
        }

    @classmethod
    def get_empty_layout(cls) -> CompoundLayoutDict:
        """ Get empty layout  """
        return {"x": None, "y": None, "clusters": {}}

    @classmethod
    def retreive_master_chebi_id(cls, chebi_id) -> dict:
        """ Get layout position matching with the CheBI id """
        cls.get_flat_data()
        if chebi_id in cls._master_ids_map:
            return cls._master_ids_map[chebi_id]
        else:
            return None
