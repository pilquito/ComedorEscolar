# Imagen base de Python
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar primero solo los archivos de dependencias para aprovechar cache de Docker
COPY requirements.txt docker-requirements.txt* /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . /app/

# Crear directorio para la base de datos SQLite si no existe
RUN mkdir -p /app/data

# Hacer ejecutable el script de inicio
RUN chmod +x /app/start.sh

# Exponer el puerto
EXPOSE 5000

# Healthcheck simple (sin requests que puede no estar instalado)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/login', timeout=5)" || exit 1

# Comando para ejecutar la aplicación usando el script de inicio
CMD ["/app/start.sh"]
