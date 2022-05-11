# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import random
from typing import List, Union

from ._layout.layout import Layout


class CompoundPosition:
    chebi_id: str = None
    x: float = None
    y: float = None
    z: float = None
    level: bool = None
    cluster: str = None
    _layout_data: dict = {}
    _compartment_offset = {}

    @classmethod
    def get_layout_data(cls):
        """ Get layout data """
        if not cls._layout_data:
            layout_data = Layout.generate()
            for key, val in layout_data.items():

                if key not in cls._layout_data:
                    cls._layout_data[key] = {}

                current_cluster = val["cluster"]
                pos = {
                    "x": val["x"],
                    "y": val["y"],
                    "level": val.get("level", 2),
                }
                cls._layout_data[key][current_cluster] = pos
                for alt_key in val.get("alt", []):
                    cls._layout_data[alt_key][current_cluster] = pos

        return cls._layout_data

    @classmethod
    def get_by_chebi_id(cls, chebi_ids: Union[str, List[str]], compartment=None):
        """ Get layout position matching with th e CheBI id """
        def rnd_offset():
            rnd_num = random.uniform(0, 1)
            return 10 if rnd_num >= 0.5 else -10

        if isinstance(chebi_ids, str):
            pos = cls.get_layout_data().get(chebi_ids, {})
        else:
            for c_id in chebi_ids:
                pos = cls.get_layout_data().get(c_id, {})
                chebi_id = c_id
                if pos:
                    break

        if pos:
            comp_pos = CompoundPosition()
            comp_pos.chebi_id = chebi_id
            comp_pos.x = pos.get("x")
            comp_pos.y = pos.get("y")
            comp_pos.z = None
            comp_pos.level = pos["level"]
            comp_pos.cluster = cluster

            # add offset of compartment
            if compartment == "e":
                comp_pos.x = None
                comp_pos.y = None
            elif compartment != "c":
                comp_pos.x += rnd_offset() * 10
                comp_pos.y += rnd_offset() * 10

            return comp_pos

        else:
            return CompoundPosition()

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "level": self.level,
            "cluster": self.cluster,
        }
