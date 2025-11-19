# Ejecutar API localmente en PowerShell
# Requisitos: Python 3.8+, instalar dependencias en un virtualenv

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# (Opcional) exportar variable si tienes parquet local:
# $env:LOCAL_PARQUET_PATH = "C:\ruta\a\carpeta_o_archivo_parquet"

uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
