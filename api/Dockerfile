FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Evitar buffering para logs
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código de la API
COPY . /app

# Puerto por defecto
EXPOSE 8000

# Comando por defecto para arrancar la API
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
