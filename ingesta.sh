#!/bin/bash
URL="https://www.datos.gov.co/api/views/gt2j-8ykr/rows.csv?accessType=DOWNLOAD"

FILE="/home/ec2-user/covid_$(date +%Y%m%d).csv"
BUCKET="s3://proyecto-covid/raw/"

curl -o "$FILE" "$URL"

aws s3 cp "$FILE" "$BUCKET"
