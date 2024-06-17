

from typing import List, TypedDict

ReactionLayoutDict = TypedDict("ReactionLayoutDict", {
    "x": str,
    "y": str,
    "points": List[dict],
})


class ReactionLayout:

    @classmethod
    def get_layout_by_rhea_id(cls, rhea_id: str) -> ReactionLayoutDict:
        return {
            "x": str,
            "y": str,
            "points": List[dict],
        }
