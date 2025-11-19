import json
import boto3
import time
import os

athena = boto3.client('athena')
S3_OUTPUT = os.environ.get('ATHENA_OUTPUT', 's3://proyecto-covid/athena-results/')
DATABASE = os.environ.get('ATHENA_DATABASE', 'covid_analytics')


def run_query(query):
    resp = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': DATABASE},
        ResultConfiguration={'OutputLocation': S3_OUTPUT}
    )
    qid = resp['QueryExecutionId']
    # Esperar terminación
    while True:
        st = athena.get_query_execution(QueryExecutionId=qid)
        s = st['QueryExecution']['Status']['State']
        if s in ('SUCCEEDED', 'FAILED', 'CANCELLED'):
            break
        time.sleep(1)
    if s != 'SUCCEEDED':
        raise Exception(f'Athena query {s}: {st["QueryExecution"]["Status"].get("StateChangeReason")}')
    res = athena.get_query_results(QueryExecutionId=qid)
    cols = [c['Name'] for c in res['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = []
    # Saltar fila de headers
    for r in res['ResultSet']['Rows'][1:]:
        vals = [v.get('VarCharValue') for v in r.get('Data', [])]
        row = {k: v for k, v in zip(cols, vals)}
        rows.append(row)
    return rows


def handler(event, context):
    params = (event.get('queryStringParameters') or {})
    dept = params.get('departamento')
    if dept:
        safe = dept.replace("'", "''")
        query = f"SELECT * FROM covid_summary WHERE nombre_departamento = '{safe}' LIMIT 100"
    else:
        query = "SELECT nombre_departamento, casos_totales, fallecidos, recuperados FROM covid_summary ORDER BY casos_totales DESC LIMIT 10"
    try:
        rows = run_query(query)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(rows)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
