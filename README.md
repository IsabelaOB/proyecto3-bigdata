<img width="1499" height="604" alt="image" src="https://github.com/user-attachments/assets/5ba1661e-6e48-4844-8521-51b18cbc14ba" /><img width="1495" height="599" alt="image" src="https://github.com/user-attachments/assets/b1d1872b-caa7-40de-a25d-d969ae699365" />Proyecto 3 – Arquitectura Batch para Big Data (COVID-19 Colombia)
Universidad EAFIT
ST0263 – Tópicos Especiales en Telemática
2025-2

1. Descripción general
Este proyecto implementa una arquitectura batch completa para el procesamiento de datos de COVID-19 en Colombia, siguiendo todas las etapas del ciclo de vida de un proceso analítico:

Captura automatizada de datos desde:
Dataset/API del Ministerio de Salud.
Base de datos relacional AWS RDS (PostgreSQL).
Ingesta automática hacia un Data Lake en Amazon S3 (zona Raw).

Procesamiento distribuido con Apache Spark sobre EMR:
ETL para limpieza y unificación de datos.
Análisis y agregación de datos.
Almacenamiento de resultados en zonas Trusted y Refined.
Consulta analítica mediante Amazon Athena.
Pipeline completamente automatizado usando Steps en EMR.
Esta solución corresponde al diseño estándar de una arquitectura Batch en la nube, cumpliendo los requisitos del proyecto.

2. Arquitectura implementada
La arquitectura se compone de las siguientes etapas:
Captura
Datos COVID descargados automáticamente desde la API gubernamental.
Datos hospitalarios exportados desde RDS con una instrucción COPY.
Ingesta
Archivos CSV enviados automáticamente a S3/Raw.
Procesamiento (EMR)
Step 1: ETL (limpieza, unión, normalización).
Step 2: Análisis (agregaciones, métricas).
Almacenamiento

Trusted: resultados limpios y consolidados.

Refined: resultados analíticos finales.

Consulta

Amazon Athena sobre los datos Refined

3. Estructura del repositorio
proyecto3-bigdata/
│
├── ingesta.sh                  # Descarga diaria de COVID y carga a RAW
├── ingesta.log                 # Registro de ejecución de ingesta
│
├── export_hospitales.sh        # Exporta RDS → RAW
├── export_hospitales.log       # Registro de exportación
│
├── etl_covid.py                # ETL Spark para crear zona Trusted
├── etl_analysis.py             # Análisis Spark para crear zona Refined
│
└── run_pipeline.sh             # Pipeline completo de EMR (Steps automáticos)

4. Ingesta automática de datos
4.1. Ingesta desde la API del Ministerio

Script:ingesta.sh
<img width="1495" height="599" alt="image" src="https://github.com/user-attachments/assets/f484e434-c2a3-4b36-be85-6ef0a341a4b0" />

Funciones:

Descarga del conjunto de datos de COVID en formato CSV.

Generación de nombre dinámico con fecha.

Carga automática al bucket S3 en la ruta:

s3://proyecto-covid/raw/

4.2. Ingesta desde RDS PostgreSQL

Script:export_hospitales.sh
<img width="1491" height="637" alt="image" src="https://github.com/user-attachments/assets/fb8cc908-7fb1-49b1-ab8b-dd383526da72" />

Funciones:

Ejecución de COPY info_hospitales TO '/tmp/info_hospitales_YYYYMMDD.csv' CSV HEADER.

Envío automático del archivo exportado a S3.

5. Procesamiento con Apache Spark en EMR
5.1. ETL (Raw → Trusted)
<img width="1495" height="638" alt="image" src="https://github.com/user-attachments/assets/7c334d5a-711d-48e7-a337-7f2a296cb38b" />

Script:etl_covid.py

Operaciones realizadas:

Lectura de archivos CSV desde Raw.

Limpieza básica (eliminación de nulos críticos).

Unión de COVID con capacidad hospitalaria.

Escritura de datos consolidados en formato Parquet en la zona Trusted:

s3://proyecto-covid/trusted/covid_final_joined/

5.2. Análisis (Trusted → Refined)
Script:etl_analysis.py
<img width="1499" height="604" alt="image" src="https://github.com/user-attachments/assets/645454b0-33b4-4438-b6e2-6a576a5b80b1" />

Genera métricas analíticas:

Casos totales.

Fallecidos.

Recuperados.

Tasa estimada de ocupación de camas por departamento.

Resultado almacenado en:

s3://proyecto-covid/refined/covid_summary/

6. Automatización del pipeline completo
Script:run_pipeline.sh
<img width="1496" height="543" alt="image" src="https://github.com/user-attachments/assets/cb6c9433-72fe-4aeb-a89c-b508cd471343" />

Este script se ejecuta de forma automática:

Creación del clúster EMR.

Ejecución del Paso 1 (ETL).

Ejecución del Paso 2 (análisis).

Terminación automática del clúster.

Ejemplo real de ejecución:

"StepIds": ["s-027851417W95W5OZGJC8", "s-08522522AWLXSFKTN95Q"]
Pipeline lanzado en cluster: j-2AFE9AUE5UHLC


Cumple con el requisito obligatorio de automatizar la ejecución del ciclo de vida completo del procesamiento.

7. Consulta analítica con Athena

Se creó la base:

CREATE DATABASE covid_analytics;


Tabla externa:

covid_analytics.covid_summary
<img width="1484" height="651" alt="image" src="https://github.com/user-attachments/assets/561f59da-7097-4c42-9d6b-ba860fabe989" />
<img width="1495" height="653" alt="image" src="https://github.com/user-attachments/assets/98280da7-f891-4336-a57e-47dfd1954cfa" />
<img width="1181" height="648" alt="image" src="https://github.com/user-attachments/assets/0d720afb-09e2-42f1-9354-5147ac013faf" />


Consulta de ejemplo:

SELECT nombre_departamento, casos_totales, fallecidos, recuperados
FROM covid_analytics.covid_summary
ORDER BY casos_totales DESC
LIMIT 10;


Athena permite verificar la consistencia de los datos generados en la zona Refined.

8. Sobre API Gateway y Lambda

El requisito del proyecto incluye la posibilidad de exponer los datos mediante una API.
Sin embargo, en AWS Academy (VocLabs) existen restricciones que impiden crear roles y ejecutar funciones Lambda debido a políticas que bloquean:

iam :CreateRole

iam :AttachRolePolicy

lambda :InvokeFunction

lambda :ListFunctions

Esto es imposible de implementar API Gateway y Lambda en este entorno.
Se entrega el código necesario, pero el despliegue no se puede realizar debido a limitaciones de la plataforma.

9. Ejecución del pipeline

En una instancia EC2 con credenciales configuradas:

chmod +x run_pipeline.sh
./run_pipeline.sh


Esto se ejecuta de manera automática:

Descarga de COVID

Exportación desde RDS

ETL → Confiable

Análisis → Refinado

Resultados disponibles para Athena
