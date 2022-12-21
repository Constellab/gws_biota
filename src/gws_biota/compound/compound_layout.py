# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import copy
import json
import os
from pathlib import Path
from typing import Dict, List, TypedDict, Union

from gws_core import BadRequestException

from .compound_cluster import CompoundCluster, CompoundClusterDict

CompoundLayoutDict = TypedDict("CompoundLayoutDict", {
    "x": str,
    "y": str,
    "clusters": List[dict],
})


class CompoundLayout:
    """ CompoundLayout """

    X_LIMIT = 4000
    Y_LIMIT = 4000
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

    @classmethod
    def get_db_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "./_layout/")

    @classmethod
    def get_cluster_path(cls, cluster_id):
        return os.path.join(cls.get_db_path(), cluster_id)

    @ classmethod
    def generate(cls, db_path: str = None, force: bool = False):
        """ Generate positions """
        if cls._is_generated:
            if not force:
                return cls._data

        if not db_path:
            db_path = cls.get_db_path()

        data = {}

        try:
            # loads for all .json files
            for root, _, files in os.walk(db_path):
                for file in files:
                    if file.endswith(".json") and file != "__centroid__.json":
                        cluster = CompoundCluster.from_file(os.path.join(root, file))
                        cls._clusters.append(cluster)
        except Exception as err:
            raise BadRequestException(f"An error occur when parsing layout files. Message {err}") from err

        for cluster in cls._clusters:
            cluster_data = cluster.generate()
            for comp_id in cluster_data:
                if comp_id not in data:
                    data[comp_id] = {}

                cluster_id = cluster_data[comp_id]["id"]
                data[comp_id][cluster_id] = cluster_data[comp_id]

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
            "clusters": clusters  # copy.deepcopy(clusters),
        }

        for c_name in position["clusters"]:
            position["clusters"][c_name]["alt"] = None

        return position

    @classmethod
    def get_empty_layout(cls) -> CompoundLayoutDict:
        """ Get empty layout  """
        return {"x": None, "y": None, "clusters": {}}

    @classmethod
    def get_biomass_layout(cls, is_biomass=False) -> CompoundLayoutDict:
        """ Create biomass layout """

        if is_biomass:
            x = None
            y = None
        else:
            x = None
            y = None

        return {
            "x": x,
            "y": y,
            "level": 1,
            "clusters": {
                "biomass": {
                    "x": x,
                    "y": y,
                    "level": 1,
                    "id": "biomass",
                    "name": "biomass",
                    "pathway": "biomass"
                }
            }
        }

    @classmethod
    def retreive_master_chebi_id(cls, chebi_id) -> dict:
        """ Get layout position matching with the CheBI id """
        cls.get_flat_data()
        if chebi_id in cls._master_ids_map:
            return cls._master_ids_map[chebi_id]
        else:
            return None

    @classmethod
    def update_compound_layout(cls, chebi_id, cluster_id, level, x, y):
        db_path = cls.get_db_path()
        cluster_path = os.path.join(db_path, cluster_id)
        try:
            # update all .json files in the cluster
            for dirpath, _, filenames in os.walk(cluster_path):
                for file in filenames:
                    if file.endswith(".json") and file != "__centroid__.json":
                        cls._update_compound_layout_in_file(
                            os.path.join(dirpath, file),
                            chebi_id, cluster_id, level, x, y)
        except Exception as err:
            raise BadRequestException(f"An error occur when parsing layout files. Message {err}") from err

    @classmethod
    def _update_compound_layout_in_file(cls, file_path, chebi_id, cluster_id, level, x, y):
        with open(file_path, 'r', encoding="utf-8") as fp:
            content = json.load(fp)

        found = False
        if chebi_id not in content["data"]:
            for current_chebi_id, data in content["data"].items():
                if chebi_id in data.get("alt", []):
                    chebi_id = current_chebi_id
                    found = True
                    break
        else:
            found = True

        if found:
            x, y = CompoundCluster.convert_position_from_view_to_db(cluster_id, x, y)
            content["data"][chebi_id]["x"] = x
            content["data"][chebi_id]["y"] = y
            content["data"][chebi_id]["level"] = level
            p = Path(file_path)
            updated_file_path = os.path.join(p.parent, p.stem + ".json")
            with open(updated_file_path, 'w', encoding="utf-8") as fp:
                json.dump(content, fp, indent=4)
