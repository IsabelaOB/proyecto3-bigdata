import os
import json
import time
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, Query
import boto3
import pandas as pd

app = FastAPI(title="Covid Summary API (local)")

ATHENA_OUTPUT = os.environ.get('ATHENA_OUTPUT', 's3://proyecto-covid/athena-results/')
ATHENA_DATABASE = os.environ.get('ATHENA_DATABASE', 'covid_analytics')
LOCAL_PARQUET = os.environ.get('LOCAL_PARQUET_PATH')  # e.g., ./data/covid_summary/

athena = boto3.client('athena')


def run_athena_query(query: str) -> List[Dict]:
    resp = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
    )
    qid = resp['QueryExecutionId']
    while True:
        st = athena.get_query_execution(QueryExecutionId=qid)
        s = st['QueryExecution']['Status']['State']
        if s in ('SUCCEEDED', 'FAILED', 'CANCELLED'):
            break
        time.sleep(1)
    if s != 'SUCCEEDED':
        reason = st['QueryExecution']['Status'].get('StateChangeReason')
        raise RuntimeError(f'Athena error {s}: {reason}')
    res = athena.get_query_results(QueryExecutionId=qid)
    cols = [c['Name'] for c in res['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = []
    for r in res['ResultSet']['Rows'][1:]:
        vals = [v.get('VarCharValue') for v in r.get('Data', [])]
        rows.append({k: v for k, v in zip(cols, vals)})
    return rows


def read_local_parquet(limit: int = 10) -> List[Dict]:
    path = LOCAL_PARQUET
    if not path:
        raise FileNotFoundError('LOCAL_PARQUET_PATH not set')
    # Support directory or single file
    if os.path.isdir(path):
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.parquet')]
        if not files:
            raise FileNotFoundError(f'No parquet files in {path}')
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    else:
        if not os.path.exists(path):
            raise FileNotFoundError(f'{path} not found')
        df = pd.read_parquet(path)
    df = df.sort_values('casos_totales', ascending=False)
    out = df.head(limit)[['nombre_departamento', 'casos_totales', 'fallecidos', 'recuperados']]
    return out.fillna('').to_dict(orient='records')


@app.get('/covid-summary')
def covid_summary(departamento: Optional[str] = Query(None, description='Nombre departamento')):
    """Devuelve top 10 por casos o filas del departamento si se especifica.

    Usa `LOCAL_PARQUET_PATH` si está definido y existe; de lo contrario usa Athena.
    """
    if LOCAL_PARQUET:
        try:
            if departamento:
                rows = read_local_parquet(limit=100)
                # filtrar localmente
                filtered = [r for r in rows if r.get('nombre_departamento') == departamento]
                return filtered
            else:
                return read_local_parquet(limit=10)
        except Exception as e:
            # si falla lectura local, fallback a Athena
            pass

    # Athena fallback
    if departamento:
        safe = departamento.replace("'", "''")
        query = f"SELECT * FROM covid_summary WHERE nombre_departamento = '{safe}' LIMIT 100"
    else:
        query = "SELECT nombre_departamento, casos_totales, fallecidos, recuperados FROM covid_summary ORDER BY casos_totales DESC LIMIT 10"
    try:
        return run_athena_query(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
