#!/bin/bash
set -e

QUERY_FILE="sql/athena_create_tables.sql"
OUTPUT='s3://proyecto-covid/athena-results/'

if [ ! -f "$QUERY_FILE" ]; then
  echo "Falta $QUERY_FILE"
  exit 1
fi

QUERY=$(sed ':a;N;$!ba;s/\n/ /g' "$QUERY_FILE")

QUERY_EXEC_ID=$(aws athena start-query-execution --query-string "$QUERY" --result-configuration OutputLocation=$OUTPUT --query 'QueryExecutionId' --output text)

echo "QueryExecutionId: $QUERY_EXEC_ID"

STATE=""
while [ "$STATE" != "SUCCEEDED" ]; do
  sleep 2
  STATE=$(aws athena get-query-execution --query-execution-id $QUERY_EXEC_ID --query 'QueryExecution.Status.State' --output text)
  echo "State: $STATE"
  if [ "$STATE" = "FAILED" ] || [ "$STATE" = "CANCELLED" ]; then
    aws athena get-query-execution --query-execution-id $QUERY_EXEC_ID --output json
    exit 1
  fi
done

echo "DDL ejecutado correctamente."
