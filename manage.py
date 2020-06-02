#
# Core GENA manage module
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com
#

import sys
import os
import unittest
import argparse
import uvicorn
from pathlib import Path
# load prism and current module
__cdir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(__cdir__,"./"))                        # -> load hello tests
sys.path.append(os.path.join(__cdir__,"./src"))                     # -> load hello module
sys.path.append(os.path.join(__cdir__,"./databases_input"))         # -> load databases_input folder
sys.path.append(os.path.join(__cdir__,"../chebi-py/src"))           # -> load chebi module
sys.path.append(os.path.join(__cdir__,"../rhea-py/src"))            # -> load rhea module
sys.path.append(os.path.join(__cdir__,"../../prod/gws-py/src"))     # -> load gws module


# set settings
from gws.settings import Settings
Settings.add_statics({
    '/static/hello'   : os.path.join(__cdir__, './src/static/hello')
})

Settings.init(dict(
    app_dir         = __cdir__,
    app_host        = 'localhost',
    app_port        = 3000,
    db_dir          = __cdir__,
    db_name         = 'db.sqlite3',     # ':memory:'
    is_test         = False,
))

#Création d'un nouveau paramètres 

from gws.prism.manage import manage

if __name__ == "__main__":
    manage()