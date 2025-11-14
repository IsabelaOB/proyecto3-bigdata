#!/bin/bash
set -e

FECHA=$(date +%Y%m%d)

sudo -u postgres psql -d covid_db -c "\COPY info_hospitales TO '/tmp/info_hospitales_${FECHA}.csv' CSV HEADER"

aws s3 cp "/tmp/info_hospitales_${FECHA}.csv" "s3://proyecto-covid/raw/info_hospitales_${FECHA}.csv"
