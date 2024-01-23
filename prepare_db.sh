#!/bin/bash

# This script is used to export the biota database, zip it to upload it
# to the cloud S3 server to declare a new version of the DB. 
# It is made to be used in the docker container of the bioate database.
# Once done, the zip file is available in the docker container and can be
# copied to the S3 server in OVH client Gencovery, bucket gws_biota.
apt update

apt install -y zip

cp -r /var/lib/mysql/ mariadb

zip -r /var/lib/mariadb.zip /var/lib/mariadb/