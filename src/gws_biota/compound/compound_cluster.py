# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
from pathlib import Path
from typing import Dict, List, TypedDict

from gws_core import BadRequestException, StringHelper

GRID_SCALE = 3
GOLBAL_CENTER = {"x": 719, "y": 513}  # Pyruvate is the center of the world!

# SHIFTS = {
#     "xenobiotic_biodegradation": {"x": -300, "y": 0},
#     "energy_metabolism": {"x": -300, "y": 0},
#     "lipid_metabolism": {"x": -400, "y": 0},
#     "carbohydrate_metabolism": {"x": 0, "y": 0},
#     "glycan_metabolism": {"x": 20, "y": 0},
#     "amino_acid_metabolism": {"x": 200, "y": 150},
#     "nucleotide_metabolism": {"x": 200, "y": 0},
#     "vitamin_and_cofactor_metabolism": {"x": 500, "y": 0},
#     "other_secondary_metabolite_metabolism": {"x": 400, "y": 0},
#     "terpenoid_and_polyketide_metabolism": {"x": 400, "y": 0},
#     "urea_cycle": {"x": 200, "y": 0}
# }

CompoundClusterDict = TypedDict("CompoundClusterDict", {
    "pathway": List[dict],
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

    _id: str = None
    _name: str = None
    _pathway: str = None
    _data: Dict[str, Dict] = None
    _centroid: dict = None
    _level: int = 2

    def __init__(self, id, name, pathway, data: Dict, centroid: Dict = None):
        if not isinstance(data, dict):
            raise BadRequestException("The data must be a dict")
        self._id = id
        self._name = name
        self._pathway = pathway
        self._data = data
        self._centroid = centroid

    @property
    def pathway(self):
        return self._pathway

    @property
    def data(self):
        return self._data

    # -- C --

    @property
    def centroid(self):
        return self._centroid

    @classmethod
    def convert_position_from_view_to_db(cls, cluster_name, x, y):
        """ Convert the position of a cluster compound from the View to the DB """

        centroid = cls.load_centroid_data_from_cluster_name(cluster_name)
        try:
            x = float(x)
            y = float(y)
            x_shift = (GOLBAL_CENTER["x"] - centroid["x"])
            y_shift = (GOLBAL_CENTER["y"] - centroid["y"])
            x = (x/GRID_SCALE + x_shift) if isinstance(x, (float, int)) else 0
            y = (y/GRID_SCALE + y_shift) if isinstance(y, (float, int)) else 0
            return x, y
        except:
            return 0, 0

    @classmethod
    def convert_position_from_db_to_view(cls, cluster_name, x, y):
        """ Convert the position of a cluster compound from the DB to the View """

        centroid = cls.load_centroid_data_from_cluster_name(cluster_name)
        try:
            x = float(x)
            y = float(y)
            x_shift = (GOLBAL_CENTER["x"] - centroid["x"])
            y_shift = (GOLBAL_CENTER["y"] - centroid["y"])
            x = GRID_SCALE*(x - x_shift) if isinstance(x, (float, int)) else 0
            y = GRID_SCALE*(y - y_shift) if isinstance(y, (float, int)) else 0
            return x, y
        except:
            return 0, 0

    # -- F --

    @ classmethod
    def from_file(cls, file_path) -> 'CompoundCluster':
        """ Create a CompoundCluster using a json data file """
        with open(file_path, "r", encoding="utf-8") as fp:
            try:
                cdata = json.load(fp)
            except Exception as err:
                raise BadRequestException(f'Cannot load the json file "{file_path}"') from err

            # load centroid
            p = Path(file_path)
            parent_folder = p.parent  # (file_path.split("/"))[-2]
            centroid_data = cls.load_centroid_data_from_folder(str(parent_folder))

            return CompoundCluster(
                id=cdata["id"],
                name=cdata["name"],
                pathway=cdata["pathway"],
                data=cdata["data"],
                centroid=centroid_data)

    # -- L --

    @classmethod
    def load_centroid_data_from_cluster_name(cls, cluster_name):
        from .compound_layout import CompoundLayout
        cluster_path = CompoundLayout.get_cluster_path(cluster_name)
        return cls.load_centroid_data_from_folder(cluster_path)

    @classmethod
    def load_centroid_data_from_folder(cls, folder):
        centroid_file = os.path.join(folder, "__centroid__.json")
        if not os.path.exists(centroid_file):
            centroid_file = os.path.join(folder, "../__centroid__.json")
        if not os.path.exists(centroid_file):
            raise BadRequestException(f'No centroid file found for folder {folder}')

        with open(centroid_file, "r", encoding="utf-8") as fp:
            try:
                cdata = json.load(fp)
            except Exception as err:
                raise BadRequestException(f'Cannot load the centroid file "{centroid_file}"') from err

        return cdata

    # -- G --

    def generate(self):
        """ Generate positions """
        data = {}
        for comp_id, comp_data in self._data.items():
            comp_data["id"] = self._id
            comp_data["name"] = self._name
            comp_data["pathway"] = self._pathway
            data[comp_id] = comp_data
        return data

    # -- S --

    def set_position(self, centroid):
        """ Set centroid """
        self._centroid = centroid
