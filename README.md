Proyecto 3 – Arquitectura Batch para Big Data (COVID-19 Colombia)
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
<img width="1170" height="363" alt="image" src="https://github.com/user-attachments/assets/c4db1e89-f562-4da2-917e-8f25f5916a6c" />

En una instancia EC2 con credenciales configuradas:

chmod +x run_pipeline.sh
./run_pipeline.sh


Esto se ejecuta de manera automática:

Descarga de COVID

Exportación desde RDS

ETL → Confiable

Análisis → Refinado

Resultados disponibles para Athena

**Despliegue y ejecución (resumen rápido)**

- **Requisitos**: AWS CLI configurado con credenciales (perfil por defecto), permisos para crear clusters EMR y S3 con bucket `proyecto-covid`.
- **Ejecutar pipeline (local/EC2)**: dar permisos y lanzar `run_pipeline.sh` desde una máquina con AWS CLI configurado:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

- **Notas sobre `run_pipeline.sh`**: los Steps añadidos usan `spark-submit` en `--deploy-mode cluster` (--master yarn). Asegúrate de que los scripts Spark (`s3://proyecto-covid/scripts/etl_covid.py` y `etl_analysis.py`) estén disponibles en ese bucket y sean ejecutables por el cluster.

- **Crear tabla en Athena**: se incluye un script DDL en `sql/athena_create_tables.sql`. Ejecuta este SQL en la consola de Athena o mediante CLI para crear la base y tabla externa apuntando a `s3://proyecto-covid/refined/covid_summary/`.

```sql
-- desde la carpeta del repo
aws s3 cp sql/athena_create_tables.sql s3://proyecto-covid/scripts/athena_create_tables.sql
-- (Luego en Athena: ejecutar el contenido de sql/athena_create_tables.sql)
```

Si prefieres que cree la tabla desde la CLI usando Athena directamente, puedo añadir un ejemplo con `aws athena start-query-execution`.
 
**Automatizar DDL desde la CLI**

Incluí un script para ejecutar el DDL de Athena desde una máquina con `aws` CLI:

```bash
chmod +x scripts/create_athena_table.sh
./scripts/create_athena_table.sh
```

Este script ejecuta `sql/athena_create_tables.sql` y espera a que la ejecución termine. Asegúrate de que el bucket `s3://proyecto-covid/athena-results/` exista o cámbialo en el script.

**API (Lambda + API Gateway) - despliegue rápido con SAM**

He incluido una función Lambda y una plantilla SAM en la carpeta `api/` que expone un endpoint GET `/covid-summary`.

- **Pre-requisitos**: `aws` CLI configurado, `sam` CLI instalado y permisos para crear Lambda, API Gateway y roles.

- **Pasos de despliegue**:

```bash
cd api
sam build
sam deploy --guided
```

En la fase `--guided` define el stack name, región y confirma la creación de recursos. La Lambda usa Athena para ejecutar consultas y devuelve JSON. Puedes probar la API desde la consola de API Gateway o con `curl`.

Ejemplo de consulta (devolverá top 10 departamentos por casos):

```bash
curl https://{API_ID}.execute-api.{region}.amazonaws.com/Prod/covid-summary
```

Para filtrar por departamento:

```bash
curl "https://{API_ID}.execute-api.{region}.amazonaws.com/Prod/covid-summary?departamento=Antioquia"
```

Si prefieres un servicio local (FastAPI) en vez de Lambda, puedo agregarlo como alternativa para demostración local.
 
**API local alternativa (FastAPI)**

He incluido una API local en `api/` que replica el comportamiento de la Lambda. Esta opción es útil si `sam deploy` falla en AWS Academy por restricciones IAM o si necesitas una demo local.

- **Archivos**:
	- `api/fastapi_app.py` : código FastAPI.
	- `api/requirements.txt` : dependencias (`fastapi`, `uvicorn`, `boto3`, `pandas`, `pyarrow`).
	- `api/run_local.ps1` : script de ejecución para PowerShell (Windows).

- **Ejecutar localmente (PowerShell)**:

```powershell
cd api
.\run_local.ps1
```

- **Comportamiento**:
	- Si la variable de entorno `LOCAL_PARQUET_PATH` apunta a un archivo o carpeta Parquet local (por ejemplo `./data/covid_summary/`), la API leerá los Parquet localmente y responderá sin usar Athena.
	- Si no hay Parquet local, la API hará consultas a Athena usando las mismas consultas que la Lambda.

Ejemplo de llamada local:

```bash
curl "http://localhost:8000/covid-summary"
curl "http://localhost:8000/covid-summary?departamento=Antioquia"
```

**Ejecutar la API en Docker**

Se incluye un `Dockerfile` en `api/` para ejecutar la API local dentro de un contenedor.

1) Construir la imagen:

```bash
cd api
docker build -t covid-summary-api:latest .
```

2) Ejecutar el contenedor (puerto 8000):

```bash
docker run --rm -p 8000:8000 \
	-e LOCAL_PARQUET_PATH="/data/covid_summary" \
	-v /ruta/local/a/parquets:/data/covid_summary \
	covid-summary-api:latest
```

Notas:
- Si quieres que la API use Parquet local dentro del contenedor, monta la carpeta con `-v /ruta/local/a/parquets:/data/covid_summary` y pasa la variable `LOCAL_PARQUET_PATH=/data/covid_summary`.
- Si la variable `LOCAL_PARQUET_PATH` no está definida o los Parquet no existen, la API consultará Athena (requiere credenciales AWS en el entorno del contenedor o usar un role de IAM en ECS).
