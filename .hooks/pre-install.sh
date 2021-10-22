# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


# Pre-installation script executed before server installation

# apt-get -y install jq
# data_dir="/data/gws_biota/sqlite3"
# sqlite3_file="${data_dir}/gws_biota.sqlite3"
# FILE_DIR=$(dirname "$0")
# sqlite3_db_url=`jq '.variables."gws_biota:sqlite3db_url"' ${FILE_DIR}/../settings.json | sed -e 's/^"//' -e 's/"$//'`

# echo $sqlite3_db_url
# if [ ! -f "$sqlite3_file" ]; then
#     if [ ! -d "$data_dir" ]; then
#         mkdir -p $data_dir
#     fi

#     curl $sqlite3_db_url -o "${sqlite3_file}.zip"
#     unzip -p "${sqlite3_file}.zip" > "${sqlite3_file}"
#     rm -f "${sqlite3_file}.zip"
# fi