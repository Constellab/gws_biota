# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from .._layout.layout import Cluster, Layout

N = None
POS = {
    # ***
    # Sterol metabolism
    # ***

    # Vitamin D2, Ergocalciferol
    "CHEBI:28934": {"x": -100,     "y": -50, "is_major": True, "alt": ["CHEBI:23937", "CHEBI:10007"]},
    # Ergosterol
    "CHEBI:16933": {"x": -105,     "y": -50, "is_major": True, "alt": ["CHEBI:42264", "CHEBI:4825", "CHEBI:14214", "CHEBI:23942"]},
    # Ergosta-5,7,22,24(28)-tetraen-3beta-ol
    "CHEBI:18249": {"x": -110,     "y": -50, "is_major": True, "alt": ["CHEBI:4824", "CHEBI:14213"]},
    # 5,7,24(28)-Ergostatrienol
    "CHEBI:80095": {"x": -115,     "y": -50, "is_major": True, "alt": [""]},
    # Episterol
    "CHEBI:50586": {"x": -120,     "y": -50, "is_major": True, "alt": [""]},
    # Fecosterol
    "CHEBI:17038": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:11663", "CHEBI:1306", "CHEBI:52361", "CHEBI:19811"]},
    # Zymosterol
    "CHEBI:18252": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:10131", "CHEBI:12172", "CHEBI:27370", "CHEBI:20646"]},
    # 5alpha-Cholesta-7,24-dien-3beta-ol
    "CHEBI:16290": {"x": -120,     "y": -50, "is_major": True, "alt": ["CHEBI:2140", "CHEBI:12171", "CHEBI:23183"]},
    # 7-Dehydrodesmosterol
    "CHEBI:27910": {"x": -125,     "y": -50, "is_major": True, "alt": ["CHEBI:2257", "CHEBI:20788"]},
    # Desmosterol
    "CHEBI:17737": {"x": -130,     "y": -50, "is_major": True, "alt": ["CHEBI:4451", "CHEBI:14130", "CHEBI:23646"]},
    # Cholesterol
    "CHEBI:16113": {"x": -130,     "y": -60, "is_major": True, "alt": ["CHEBI:41564", "CHEBI:3659", "CHEBI:13982", "CHEBI:23204"]},

    # 20alpha,22beta-Dihydroxycholesterol;
    "CHEBI:1294": {"x": -130,     "y": -70, "is_major": True, "alt": [""]},
    # Pregnenolone
    "CHEBI:16581": {"x": -130,     "y": -80, "is_major": True, "alt": ["CHEBI:14881", "CHEBI:45027", "CHEBI:8388", "CHEBI:26241", "CHEBI:86573"]},
    # Progesterone
    "CHEBI:17026": {"x": -130,     "y": -90, "is_major": True, "alt": ["CHEBI:18798", "CHEBI:45786", "CHEBI:14896", "CHEBI:26269", "CHEBI:439", "CHEBI:8453", "CHEBI:28589"]},
    # 11-Deoxycorticosterone
    "CHEBI:16973": {"x": -130,     "y": -100, "is_major": True, "alt": ["CHEBI:713", "CHEBI:39642", "CHEBI:11314", "CHEBI:19123", "CHEBI:86536"]},
    # Corticosterone
    "CHEBI:16827": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:41361", "CHEBI:3891", "CHEBI:14022", "CHEBI:19131", "CHEBI:57911"]},
    # 18-Hydroxycorticosterone
    "CHEBI:16485": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:19177", "CHEBI:11343", "CHEBI:795", "CHEBI:57789"]},
    # Aldosterone
    "CHEBI:27584": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:40919", "CHEBI:2563", "CHEBI:22306"]},

    # 17alpha-Hydroxypregnenolone
    "CHEBI:28750": {"x": -125,     "y": -80, "is_major": True, "alt": ["CHEBI:19172", "CHEBI:789"]},
    # 17alpha-Hydroxyprogesterone
    "CHEBI:17252": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:11340", "CHEBI:790", "CHEBI:11339", "CHEBI:19173"]},
    # 11-Deoxycortisol
    "CHEBI:28324": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:19124", "CHEBI:714", "CHEBI:181455"]},
    # Cortisol
    "CHEBI:17650": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:3893", "CHEBI:14023", "CHEBI:24633", "CHEBI:58221", "CHEBI:180955"]},
    # Cortisone
    "CHEBI:16962": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:3896", "CHEBI:23397", "CHEBI:14026"]},

    # 7-Dehydrocholesterol
    "CHEBI:17759": {"x": -125,     "y": -60, "is_major": True, "alt": ["CHEBI:3658", "CHEBI:13981", "CHEBI:23181"]},
    # Lathosterol
    "CHEBI:17168": {"x": -120,     "y": -50, "is_major": True, "alt": ["CHEBI:12169", "CHEBI:2138", "CHEBI:20643"]},
    # 5alpha-Cholest-8-en-3beta-ol
    "CHEBI:16608": {"x": -115,     "y": -50, "is_major": True, "alt": ["CHEBI:12170", "CHEBI:20645", "CHEBI:2139", "CHEBI:175094"]},

    # Vitamin D3
    "CHEBI:28940": {"x": -125,     "y": -70, "is_major": True, "alt": ["CHEBI:46283", "CHEBI:10008", "CHEBI:23170"]},

    # # Pregnenolone
    # "CHEBI:": {"x": -115,     "y": -50, "is_major": True, "alt": [""]},
    # # --
    # "CHEBI:": {"x": -115,     "y": -50, "is_major": True, "alt": [""]},
    # # --
    # "CHEBI:": {"x": -115,     "y": -50, "is_major": True, "alt": [""]}
}

c = Cluster(POS, position={"x": 0, "y": 0})
Layout.add_cluster(c)
