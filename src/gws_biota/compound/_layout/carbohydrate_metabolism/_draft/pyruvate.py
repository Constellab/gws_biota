# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from ..._layout.layout import Cluster, Layout

N = None
POS = {

    # ***
    # Pyruvate
    # ***

    # pyruvate
    "CHEBI:15361": {"x": 0,     "y": 0, "is_major": True, "alt": ["CHEBI:26462", "CHEBI:26466", "CHEBI:8685", "CHEBI:32816", "CHEBI:45253", "CHEBI:14987"]},
    # acetyl_CoA(4-)
    "CHEBI:57288": {"x": 0,     "y": -10, "is_major": True, "alt": ["CHEBI:22192", "CHEBI:15351", "CHEBI:13712", "CHEBI:2408", "CHEBI:40470"]},
    # (S)-lactate
    "CHEBI:16651": {"x": 30,    "y": 0, "is_major": True},
    # (R)-lactate
    "CHEBI:16004": {"x": 30,    "y": 5, "is_major": True, "alt": ["CHEBI:341", "CHEBI:18684", "CHEBI:43701", "CHEBI:11001", "CHEBI:42111", "CHEBI:42105"]},
    # lactate
    "CHEBI:24996": {"x": 30,    "y": 5, "is_major": True, "alt": []},
    # formate
    "CHEBI:15740": {"x": -40,    "y": 0, "is_major": True, "alt": ["CHEBI:14276", "CHEBI:24081"]},
    # acetate
    "CHEBI:30089": {"x": -30,     "y": -20, "is_major": True, "alt": ["CHEBI:13704", "CHEBI:22165", "CHEBI:22169", "CHEBI:40480", "CHEBI:15366", "CHEBI:2387", "CHEBI:40486"]},
    # acetyl phosphate
    "CHEBI:13711": {"x": -20,     "y": -0, "is_major": True, "alt": ["CHEBI:46262", "CHEBI:15350", "CHEBI:22191", "CHEBI:2407"]},
    # acetoacetate
    "CHEBI:13705": {"x": -20,     "y": -20, "is_major": True},
}

c = Cluster(POS, position={"x": 0, "y": 0})
Layout.add_cluster(c)
