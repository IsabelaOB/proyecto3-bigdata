Proyecto 3 – Arquitectura Batch Big Data COVID-19 (AWS)

Curso: ST0263 – Tópicos Especiales en Telemática
Fecha: 2025

Descripción del Proyecto

Este proyecto implementa una arquitectura batch completa para el procesamiento de datos reales de COVID-19 en Colombia, siguiendo todas las etapas del ciclo de vida de un proceso analítico. El procesamiento es realizado mediante Spark en Amazon EMR y los resultados analíticos finales se consultan mediante Amazon Athena. La arquitectura está totalmente automatizada mediante scripts Bash y steps en EMR.

Arquitectura general:

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/bc42cb95-05e4-4f9a-9410-9a90c05451cf" />
Componentes de la Arquitectura
Componente	Función
RDS PostgreSQL	Fuente de datos hospitalarios
Script export_hospitales.sh	Exporta datos desde RDS hacia S3 RAW
Descarga COVID automática	Obtiene datos del Ministerio de Salud en CSV
Spark ETL en EMR	Limpieza y unificación de datos → Trusted
Spark Analysis en EMR	Métricas y agregaciones → Refined
Athena	Consulta analítica
run_pipeline.sh	Orquesta todo el proceso de forma automática
Estructura de Carpetas
/raw
    covid_YYYYMMDD.csv
    info_hospitales_YYYYMMDD.csv

/trusted
    covid_final_joined/

/refined
    covid_summary/

/scripts
    etl_covid.py
    etl_analysis.py

/logs

1. Ingesta Automática (Zona Raw)
Script: export_hospitales.sh

Ruta: /home/ec2-user/export_hospitales.sh

#!/bin/bash
set -e
FECHA=$(date +%Y%m%d)
sudo -u postgres psql -d covid_db -c "\COPY info_hospitales TO '/tmp/info_hospitales_${FECHA}.csv' CSV HEADER"
aws s3 cp "/tmp/info_hospitales_${FECHA}.csv" "s3://proyecto-covid/raw/info_hospitales_${FECHA}.csv"


Función: Exporta datos desde RDS PostgreSQL y los envía automáticamente a la zona RAW en S3 sin intervención manual.

2. ETL en Spark (Zona Trusted)
Script: etl_covid.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ETL-COVID").getOrCreate()

raw_covid = "s3://proyecto-covid/raw/covid_20251113.csv"
raw_hosp = "s3://proyecto-covid/raw/info_hospitales_20251113.csv"
trusted_output = "s3://proyecto-covid/trusted/covid_final_joined/"

df_covid = spark.read.option("header", "true").csv(raw_covid)
df_hosp = spark.read.option("header", "true").csv(raw_hosp)

df_join = df_covid.join(
    df_hosp,
    df_covid["Nombre departamento"] == df_hosp["departamento"],
    "left"
)

df_join.write.mode("overwrite").parquet(trusted_output)

spark.stop()


Resultados en:
s3://proyecto-covid/trusted/covid_final_joined/

3. Análisis en Spark (Zona Refined)
Script: etl_analysis.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("COVID-ANALYSIS").getOrCreate()

trusted_path = "s3://proyecto-covid/trusted/covid_final_joined/"
refined_output = "s3://proyecto-covid/refined/covid_summary/"

df = spark.read.parquet(trusted_path)

df_summary = (
    df.groupBy("Nombre departamento","departamento","camas","ucis")
      .agg(
          F.count("*").alias("casos_totales"),
          F.sum(F.when(F.col("Estado")=="Fallecido",1).otherwise(0)).alias("fallecidos"),
          F.sum(F.when(F.col("Recuperado")=="Recuperado",1).otherwise(0)).alias("recuperados")
      )
)

df_summary.write.mode("overwrite").parquet(refined_output)
spark.stop()


Resultados en:
s3://proyecto-covid/refined/covid_summary/

4. Pipeline Automático (Cluster EMR + Steps)
Script: run_pipeline.sh
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

5. Consulta Analítica con Athena
Creación de la base
CREATE DATABASE IF NOT EXISTS covid_analytics;

Creación de la tabla
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

Ejemplo de consulta
SELECT nombre_departamento, casos_totales, fallecidos, recuperados
FROM covid_analytics.covid_summary
ORDER BY casos_totales DESC
LIMIT 10;

6. Restricciones sobre API Gateway y Lambda

El entorno AWS Academy (VocLabs) impide la creación de roles y ejecución de funciones Lambda debido a restricciones en permisos como:

iam:CreateRole
iam:AttachRolePolicy
lambda:InvokeFunction
lambda:ListFunctions


Por este motivo, no es posible desplegar API Gateway + Lambda a pesar de contar con el código necesario.

7. Ejecución del Pipeline

En una instancia EC2 con credenciales configuradas:

chmod +x run_pipeline.sh
./run_pipeline.sh


Este proceso se ejecuta automáticamente:

Descarga de datos COVID

Exportación desde RDS

ETL → Trusted

Análisis → Refined

Resultados listos para Athena
