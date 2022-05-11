# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from .._layout.layout import Cluster, Layout

# ***
# Ethanol metabolism
# ***

N = None
POS = {
    # acetaldehyde
    "CHEBI:15343": {"x": 20,     "y": 0, "is_major": True, "alt": ["CHEBI:40533", "CHEBI:13703", "CHEBI:2383", "CHEBI:22158"]},
    # ethanol
    "CHEBI:16236": {"x": 30,     "y": 0, "is_major": True, "alt": ["CHEBI:44594", "CHEBI:42377", "CHEBI:4879", "CHEBI:14222", "CHEBI:23978", "CHEBI:30878", "CHEBI:30880"]}
}

c = Cluster(POS, position={"x": 0, "y": 0})
Layout.add_cluster(c)
