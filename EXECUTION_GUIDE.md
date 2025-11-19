# Guía de Ejecución del Pipeline - Proyecto 3 (COVID)

Esta guía resume los pasos para ejecutar y validar el pipeline completo: Captura → Ingesta → ETL → Análisis → Consulta/API.
Incluye opciones para ejecución en AWS (EMR + Athena + Lambda/SAM) y alternativas locales (FastAPI + Docker) para entornos con restricciones como AWS Academy.

> Ruta del repo: `C:\Users\juanm\proyecto3-bigdata`

---

## 1. Prerrequisitos
- AWS CLI instalado y configurado (`aws configure`) con credenciales y región.
- (Opcional) SAM CLI para desplegar Lambda/API.
- Docker y Docker Compose para la demo local en contenedor.
- Python 3.8+ para ejecutar scripts locales.
- (Opcional) Spark local o acceso a EMR para ejecutar `spark-submit`.

Abre PowerShell y sitúate en el repo:
```powershell
cd C:\Users\juanm\proyecto3-bigdata
```

---

## 2. Preparación local
- Si vas a ejecutar la API localmente instala dependencias:
```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
- Asegúrate de que el bucket `s3://proyecto-covid/` exista o cambia las rutas en los scripts.

---

## 3. Ingesta de datos
### 3.1. Descarga desde la API del Ministerio
Script: `ingesta.sh` (Linux/EC2)
```bash
chmod +x ingesta.sh
./ingesta.sh
```
Este script descarga el CSV oficial y lo sube a `s3://proyecto-covid/raw/`.

### 3.2. Exportación desde RDS (Postgres)
Script: `export_hospitales.sh` (ejecutar desde EC2 o máquina cliente con `psql`):
```bash
chmod +x export_hospitales.sh
./export_hospitales.sh
```
Nota: `export_hospitales.sh` usa `
COPY` vía `psql` desde la máquina cliente. Si usas RDS asegúrate de ejecutar la copia desde una instancia que tenga acceso a la base (EC2).

---

## 4. Preparar Athena (DDL)
Archivo DDL: `sql/athena_create_tables.sql`

- Ejecuta el DDL manualmente en la consola de Athena o automatízalo con el script:
```powershell
chmod +x scripts/create_athena_table.sh
.\scripts\create_athena_table.sh
```
- El script usa `s3://proyecto-covid/athena-results/` para almacenar resultados temporales; crea el bucket si es necesario.

Consulta de ejemplo en Athena:
```sql
SELECT nombre_departamento, casos_totales, fallecidos, recuperados
FROM covid_analytics.covid_summary
ORDER BY casos_totales DESC
LIMIT 10;
```

---

## 5. Ejecutar ETL y Análisis en EMR (pipeline automático)
Los scripts Spark están en el repo: `etl_covid.py` y `etl_analysis.py`.

Asegura que los scripts estén disponibles en S3: `s3://proyecto-covid/scripts/etl_covid.py` y `etl_analysis.py`.

Lanza el pipeline (crea cluster EMR + Steps):
```powershell
chmod +x run_pipeline.sh
./run_pipeline.sh
```
El script devuelve el `ClusterId`. Revisa la consola EMR para ver logs y el estado de los steps.

### Alternativa (Spark local)
Si no tienes EMR, puedes ejecutar los scripts localmente con `spark-submit`:
```powershell
spark-submit --master local[4] etl_covid.py
spark-submit --master local[4] etl_analysis.py
```
Asegúrate de que los `trusted_path` y `refined_output` apunten a rutas accesibles (local o S3).

---

## 6. Verificar salidas
- Trusted Parquet: `s3://proyecto-covid/trusted/covid_final_joined/`
- Refined Parquet (summary): `s3://proyecto-covid/refined/covid_summary/`

Comprobar en S3:
```powershell
aws s3 ls s3://proyecto-covid/refined/covid_summary/
```

---

## 7. API (opción 1): Lambda + API Gateway (SAM)
Archivos: `api/lambda_function.py`, `api/template.yaml`.

Desplegar con SAM:
```powershell
cd api
sam build
sam deploy --guided
```
- Durante `--guided` define parámetros (stack name, región, permisos).
- La plantilla concede permisos a Athena y S3; en AWS Academy puede fallar si no se permiten operaciones IAM.

Probar la API desplegada:
```bash
curl https://{API_ID}.execute-api.{region}.amazonaws.com/Prod/covid-summary
curl "https://{API_ID}.execute-api.{region}.amazonaws.com/Prod/covid-summary?departamento=Antioquia"
```

---

## 8. API (opción 2): Demo local con FastAPI
Archivos: `api/fastapi_app.py`, `api/requirements.txt`, `api/run_local.ps1`.

Ejecutar en PowerShell:
```powershell
cd api
.\.venv\Scripts\Activate.ps1  # si usaste el virtualenv
.\run_local.ps1
# O si ya instalaste dependencias y prefieres uvicorn directo:
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

La API local hace lo siguiente:
- Si la variable de entorno `LOCAL_PARQUET_PATH` apunta a un archivo/carpeta Parquet (p.ej. `api/sample_data`), la API devolverá resultados desde Parquet local.
- Si no hay Parquet local, hará consultas a Athena (requiere credenciales AWS).

Probar localmente:
```bash
curl "http://localhost:8000/covid-summary"
curl "http://localhost:8000/covid-summary?departamento=Antioquia"
```

---

## 9. Docker y docker-compose (demo reproducible)
Se incluyen `api/Dockerfile` y `docker-compose.yml` y un generador de datos de ejemplo `scripts/generate_sample_parquet.py`.

Generar datos de muestra (usa servicio `gen`):
```powershell
docker-compose run --rm gen
```

Levantar la API con compose:
```powershell
docker-compose up --build api
```

O construir imagen manualmente:
```powershell
cd api
docker build -t covid-summary-api:latest .
# ejecutar con volumen local de parquets
docker run --rm -p 8000:8000 \
  -e LOCAL_PARQUET_PATH="/data/covid_summary" \
  -v C:\ruta\local\parquets:/data/covid_summary \
  covid-summary-api:latest
```

---

## 10. Pruebas rápidas
- Comprobar Athena (consulta SQL anterior).
- Llamar a la API (local o desplegada) y verificar que las respuestas contienen campos: `nombre_departamento`, `casos_totales`, `fallecidos`, `recuperados`.

---

## 11. Troubleshooting rápido
- `sam deploy` falla (IAM): usa la API local (FastAPI) o Docker para la demo.
- Steps EMR fallan: revisar logs en la consola EMR y comprobar que los scripts estén en `s3://proyecto-covid/scripts/`.
- Errores de S3/Athena: confirmar `aws configure` y permisos S3/Athena.
- `git push` falla: comprueba rama con `git branch`, sincroniza con `git pull --rebase origin <branch>`, resuelve conflictos y vuelve a push.

Comandos git sugeridos:
```powershell
git status
git add .
git commit -m "Cambios finales"
git pull --rebase origin development
git push origin development
```

---

## 12. Siguientes pasos recomendados
- Si tu cuenta AWS tiene limitaciones, usa Docker/FastAPI para la presentación.
- Si quieres ML opcional, puedo añadir un ejemplo con SparkML (`scripts/spark_ml_example.py`) y un Step opcional en `run_pipeline.sh`.
- Puedo preparar un `docker-compose` final que levante la API y un contenedor con un explorer simple si lo necesitas.

---

Si quieres que haga commit y push de este archivo `EXECUTION_GUIDE.md`, o que agregue el ejemplo ML ahora, dime y lo hago. ¡Listo para el siguiente paso!