#!/bin/bash
set -e

CLUSTER_ID=$(aws emr create-cluster \
  --name "ClusterCOVID-PIPELINE" \
  --release-label emr-6.15.0 \
  --applications Name=Spark \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --auto-terminate \
  --log-uri s3://proyecto-covid/logs/ \
  --query 'ClusterId' --output text)

aws emr add-steps \
  --cluster-id $CLUSTER_ID \
  --steps \
Type=Spark,Name="ETL-COVID",ActionOnFailure=CONTINUE,Args=[s3://proyecto-covid/scripts/etl_covid.py] \
Type=Spark,Name="COVID-ANALYSIS",ActionOnFailure=CONTINUE,Args=[s3://proyecto-covid/scripts/etl_analysis.py]

echo "Pipeline lanzado en cluster: $CLUSTER_ID"
