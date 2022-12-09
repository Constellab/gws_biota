# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from fastapi import Depends
from gws_core import AuthService
from gws_core.app import core_app
from pydantic import BaseModel

from .compound_layout import CompoundLayout


# Info provided by the user
class UpdateCompoundLayout(BaseModel):
    chebi_id: str
    cluster_name: str
    level: int
    x: float
    y: float


@core_app.put("/biota/compound-layout")
def update_compound_layout(
        compound_layout: UpdateCompoundLayout,
        _=Depends(AuthService.check_user_access_token)):
    """
    Update compound information like position and level directly in json files.
    """

    CompoundLayout.update_compound_layout(
        chebi_id=compound_layout.chebi_id,
        cluster_name=compound_layout.cluster_name,
        level=compound_layout.level,
        x=compound_layout.x,
        y=compound_layout.y
    )

    return compound_layout
