# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from ..._layout.layout import Cluster, Layout

N = None
POS = {

    # ***
    # Fuctose metabolism
    # ***

    # fructofuranose, D-Fructose
    "CHEBI:37721": {"x": -10,     "y": 80, "is_major": True, "alt": ["CHEBI:47424", "CHEBI:4119", "CHEBI:47424", "CHEBI:28757", "CHEBI:24110", "CHEBI:20929", "CHEBI:4119", "CHEBI:15824", "CHEBI:5172", "CHEBI:24104", "CHEBI:12923", "CHEBI:4118", "CHEBI:37714", "CHEBI:37721", "CHEBI:48095"]},
    # D-Fructose 1,6-bisphosphate
    "CHEBI:49299": {"x": -10,     "y": 60, "is_major": True, "alt": ["CHEBI:78682", "CHEBI:37736"]},

    # alpha-D-fructofuranose 1-phosphate(2-), D-fructofuranose 1-phosphate
    "CHEBI:138881": {"x": -10,    "y": 70, "is_major": True, "alt": ["CHEBI:37515", "CHEBI:20930", "CHEBI:5174"]},
}

c = Cluster(POS, position={"x": 0, "y": 0})
Layout.add_cluster(c)
