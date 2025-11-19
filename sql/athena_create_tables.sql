-- Crear base de datos (si no existe)
CREATE DATABASE IF NOT EXISTS covid_analytics;

-- Tabla externa para el summary generado por Spark (formato Parquet)
CREATE EXTERNAL TABLE IF NOT EXISTS covid_analytics.covid_summary (
  nombre_departamento string,
  departamento string,
  camas int,
  ucis int,
  casos_totales bigint,
  fallecidos bigint,
  recuperados bigint,
  tasa_ocupacion_camas_estimada double
)
STORED AS PARQUET
LOCATION 's3://proyecto-covid/refined/covid_summary/';
