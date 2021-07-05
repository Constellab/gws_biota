# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


# Pre-installation script executed before server installation

data_dir="/data/sqlite3"
sqlite3_file="${data_dir}/biota.sqlite3"

if [ ! -f "$sqlite3_file" ]; then
    curl https://share.gencovery.com/s/Eo34Y8sxgqSdSMz/download -o "${sqlite3_file}.zip"
    unzip -p "${sqlite3_file}.zip" > "${sqlite3_file}"
    rm -f "${sqlite3_file}.zip"
fi