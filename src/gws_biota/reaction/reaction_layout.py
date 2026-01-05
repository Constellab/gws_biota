

from typing import TypedDict


class ReactionLayoutDict(TypedDict):
    x: str
    y: str
    points: list[dict]


class ReactionLayout:

    @classmethod
    def get_layout_by_rhea_id(cls, rhea_id: str) -> ReactionLayoutDict:
        return {
            "x": str,
            "y": str,
            "points": list[dict],
        }
