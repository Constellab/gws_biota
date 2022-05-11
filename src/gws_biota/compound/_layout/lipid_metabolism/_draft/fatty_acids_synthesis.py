# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from ..._layout.layout import Cluster, Layout

N = None
POS = {

    # ***
    # Fatty acid synthesis
    # ***

    # malonyl-CoA(5-)
    "CHEBI:57384": {"x": -170,    "y": 30},

    # 3-Oxostearoyl-[acp]
    "CHEBI:80386": {"x": -150,    "y": 20},
    # 3-Hydroxyoctadecanoyl-[acp]
    "CHEBI:80387": {"x": -150,    "y": 10},
    # (2E)-Octadecenoyl-[acp]
    "CHEBI:80388": {"x": -150,    "y": 0},
    # Octadecanoyl-[acyl-carrier protein]
    "CHEBI:6780": {"x": -150,    "y": -10},
    # Octadecanoic acid
    "CHEBI:25629": {"x": -150,    "y": -20, "alt": ["CHEBI:28842", "CHEBI:231588", "CHEBI:45710", "CHEBI:25631"]},

    # 3-Oxohexadecanoyl-[acp]
    "CHEBI:1639": {"x": -155,    "y": 20},
    # (3R)-3-Hydroxypalmitoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -155,    "y": 10},
    # trans-Hexadec-2-enoyl-[acp]
    "CHEBI:10729": {"x": -155,    "y": 0},
    # Hexadecanoyl-[acp]
    "CHEBI:5697": {"x": -155,    "y": -10},
    # Palmitoleic acid
    "CHEBI:28716": {"x": -155,    "y": -20, "alt": ["CHEBI:7897", "CHEBI:44696", "CHEBI:25836"]},

    # 3-Oxotetradecanoyl-[acp]
    "CHEBI:1655": {"x": -160,    "y": 20},
    # (3R)-3-Hydroxytetradecanoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -160,    "y": 10},
    # trans-Tetradec-2-enoyl-[acp]
    "CHEBI:10735": {"x": -160,    "y": 0},
    # Tetradecanoyl-[acp]
    "CHEBI:50651": {"x": -160,    "y": -10, "alt": ["CHEBI:7059", "CHEBI:9476"]},
    # Tetradecanoic acid
    "CHEBI:28875": {"x": -160,    "y": -20, "alt": ["CHEBI:278516", "CHEBI:44232", "CHEBI:73168", "CHEBI:26897", "CHEBI:7056", "CHEBI:30807", "CHEBI:35292"]},

    # 3-Oxododecanoyl-[acp]
    "CHEBI:1637": {"x": -165,    "y": 20},
    # (R)-3-Hydroxydodecanoyl-[acp]
    "CHEBI:325": {"x": -165,    "y": 10},
    # trans-Dodec-2-enoyl-[acp]
    "CHEBI:10725": {"x": -165,    "y": 0},
    # Dodecanoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -165,    "y": -20, "alt": [""]},
    # Dodecanoic acid
    "CHEBI:18262": {"x": -165,    "y": -20, "alt": ["CHEBI:14187", "CHEBI:23863", "CHEBI:30805", "CHEBI:41882", "CHEBI:4680", "CHEBI:23864", "CHEBI:23865"]},

    # 3-Oxodecanoyl-[acp]
    "CHEBI:1634": {"x": -170,    "y": 20},
    # (3R)-3-Hydroxydecanoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -170,    "y": 10},
    # trans-Dec-2-enoyl-[acp]
    "CHEBI:10724": {"x": -170,    "y": 0},
    # Decanoyl-[acp]
    "CHEBI:4349": {"x": -170,    "y": -20, "alt": [""]},
    # Decanoic acid
    "CHEBI:27689": {"x": -170,    "y": -20, "alt": ["CHEBI:23570", "CHEBI:125804", "CHEBI:30813", "CHEBI:41906", "CHEBI:23572", "CHEBI:4347"]},

    # 3-Oxooctanoyl-[acp]
    "CHEBI:1646": {"x": -175,    "y": 20},
    # (3R)-3-Hydroxyoctanoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -175,    "y": 10},
    # trans-Oct-2-enoyl-[acp]
    # "CHEBI:": {"x": -175,    "y": 0},
    # Octanoyl-[acp]
    "CHEBI:7725": {"x": -175,    "y": -20, "alt": [""]},
    # Octanoic acid
    "CHEBI:28837": {"x": -175,    "y": -20, "alt": ["CHEBI:44501", "CHEBI:3373", "CHEBI:25648"]},

    # 3-Oxohexanoyl-[acp]
    "CHEBI:1642": {"x": -180,    "y": 20},
    # (R)-3-Hydroxyhexanoyl-[acp]
    "CHEBI:326": {"x": -180,    "y": 10},
    # trans-Hex-2-enoyl-[acp]
    "CHEBI:10727": {"x": -180,    "y": 0},
    # Hexanoyl-[acp]
    "CHEBI:5704": {"x": -180,    "y": -20, "alt": [""]},

    # Acetoacetyl-[acp]
    "CHEBI:2393": {"x": -185,    "y": 20},
    # (3R)-3-Hydroxybutanoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -185,    "y": 10},
    # But-2-enoyl-[acyl-carrier protein]
    # "CHEBI:": {"x": -185,    "y": 0},
    # Butyryl-[acp]
    "CHEBI:3247": {"x": -185,    "y": -20, "alt": [""]},

    # Linoleoyl-CoA
    "CHEBI:15530": {"x": -190,    "y": 20, "alt": ["CHEBI:6480", "CHEBI:14516", "CHEBI:25049"]},
    # gamma-Linolenoyl-CoA
    "CHEBI:15508": {"x": -190,    "y": 10, "alt": ["CHEBI:10574", "CHEBI:12405", "CHEBI:24198"]},
    # (4Z,7Z,10Z,13Z,16Z)-Docosapentaenoyl-CoA
    # "CHEBI:76450": {"x": -190,    "y": 0},
    # (6Z,9Z,12Z,15Z,18Z)-Tetracosapentaenoyl-CoA
    "CHEBI:63546": {"x": -190,    "y": -20, "alt": [""]},
    # (10Z,13Z,16Z,19Z,22Z)-Octacosapentaenoyl-CoA
    # "CHEBI:": {"x": -190,    "y": -20, "alt": [""]},
}

c = Cluster(POS, position={"x": 0, "y": 0})
Layout.add_cluster(c)
