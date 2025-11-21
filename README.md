Proyecto 3 – Arquitectura Batch Big Data COVID-19 (AWS)

Curso: ST0263 – Tópicos Especiales en Telemática
Fecha: 2025

Descripción del Proyecto

Este proyecto implementa una arquitectura batch completa para el procesamiento de datos de COVID-19 en Colombia. Incluye todas las etapas del ciclo de vida de un proceso analítico, con automatización total mediante scripts y pasos en EMR.

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/bc42cb95-05e4-4f9a-9410-9a90c05451cf" />

El procesamiento se realiza en Amazon EMR (Spark), los datos se almacenan en Amazon S3, y los resultados finales son consultados mediante Amazon Athena.

1. Arquitectura General
Componentes
Componente	Función
RDS PostgreSQL	Datos hospitalarios
export_hospitales.sh	Envía datos a S3 Raw
Descarga automática COVID	Ingesta a S3 Raw
EMR (Spark)	ETL y análisis
Trusted (Parquet)	Datos limpios y unificados
Refined (Parquet)	Métricas y agregaciones
Athena	Consulta analítica
run_pipeline.sh	Automatiza el proceso
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

2. Ingesta Automática (Raw)
Script: export_hospitales.sh

Ubicación en EC2: /home/ec2-user/export_hospitales.sh

#!/bin/bash
set -e
FECHA=$(date +%Y%m%d)
sudo -u postgres psql -d covid_db -c "\COPY info_hospitales TO '/tmp/info_hospitales_${FECHA}.csv' CSV HEADER"
aws s3 cp "/tmp/info_hospitales_${FECHA}.csv" "s3://proyecto-covid/raw/info_hospitales_${FECHA}.csv"


Función: Captura los datos del RDS y los envía automáticamente a la zona Raw.

3. ETL en Spark (Zona Trusted)
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

4. Análisis en Spark (Zona Refined)
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

5. Automatización del Pipeline Completo
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


Ejemplo Real de Ejecución

"StepIds": ["s-027851417W95W5OZGJC8", "s-08522522AWLXSFKTN95Q"]
Pipeline lanzado en cluster: j-2AFE9AUE5UHLC

6. Consulta Analítica con Athena
Crear Base de Datos
CREATE DATABASE IF NOT EXISTS covid_analytics;

Crear Tabla Externa
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

Consulta Ejemplo
SELECT nombre_departamento, casos_totales, fallecidos, recuperados
FROM covid_analytics.covid_summary
ORDER BY casos_totales DESC
LIMIT 10;

Evidencias
<img width="1484" height="651" alt="image" src="https://github.com/user-attachments/assets/561f59da-7097-4c42-9d6b-ba860fabe989" /> <img width="1495" height="653" alt="image" src="https://github.com/user-attachments/assets/98280da7-f891-4336-a57e-47dfd1954cfa" /> <img width="1181" height="648" alt="image" src="https://github.com/user-attachments/assets/0d720afb-09e2-42f1-9354-5147ac013faf" />
7. Restricciones: API Gateway y Lambda

AWS Academy (VocLabs) restringe las políticas necesarias para desplegar Lambda y API Gateway:

iam:CreateRole

iam:AttachRolePolicy

lambda:InvokeFunction

lambda:ListFunctions

Esto hace imposible la implementación real en esta plataforma. Se entrega el código, pero el despliegue no es posible.

8. Ejecución Manual del Pipeline

Desde una instancia EC2 con credenciales configuradas:

chmod +x run_pipeline.sh
./run_pipeline.sh

<img width="1170" height="363" alt="image" src="https://github.com/user-attachments/assets/c4db1e89-f562-4da2-917e-8f25f5916a6c" />
