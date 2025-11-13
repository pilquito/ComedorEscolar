#!/bin/bash
# Script de inicio para Sistema de Gestión de Comedor Escolar
# Compatible con Docker y Dockploy

set -e

echo "========================================="
echo "Sistema de Gestión de Comedor Escolar"
echo "Iniciando aplicación..."
echo "========================================="

# Crear directorio de datos si no existe
mkdir -p /app/data

# Verificar variables de entorno obligatorias
if [ -z "$SESSION_SECRET" ]; then
    echo "⚠️  ADVERTENCIA: SESSION_SECRET no está configurado"
    echo "Generando SESSION_SECRET temporal (NO USAR EN PRODUCCIÓN)"
    export SESSION_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
fi

# Configurar zona horaria
if [ ! -z "$TZ" ]; then
    echo "🌍 Configurando zona horaria: $TZ"
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
    echo $TZ > /etc/timezone
fi

# Mostrar configuración (sin mostrar secretos)
echo ""
echo "📋 Configuración de la aplicación:"
echo "   - Flask Environment: ${FLASK_ENV:-production}"
echo "   - Database Path: ${DATABASE_PATH:-/app/data/cafeteria.db}"
echo "   - Workers: ${WORKERS:-4}"
echo "   - Timeout: ${TIMEOUT:-120}s"
echo "   - Timezone: ${TZ:-Europe/Madrid}"
echo ""

# Verificar permisos del directorio de datos
echo "Verificando permisos de /app/data..."
ls -la /app/data || echo "Directorio no existe, se creara"
touch /app/data/test.txt && rm /app/data/test.txt && echo "✅ Permisos OK" || echo "❌ Sin permisos de escritura"

# Test rápido de importación
echo "Verificando que Python puede importar la app..."
python3 -c "import sys; print('Python version:', sys.version)" || exit 1
python3 -c "from app import app; print('✅ App importada correctamente')" || {
    echo "❌ ERROR: No se puede importar la app"
    python3 -c "from app import app" 2>&1
    exit 1
}

echo ""
echo "========================================="
echo "🚀 Iniciando servidor con Gunicorn..."
echo "========================================="
echo "Bind: 0.0.0.0:${PORT:-5000}"
echo "Workers: ${WORKERS:-4}"
echo ""

# Ejecutar Gunicorn con configuración verbose
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${WORKERS:-4} \
    --threads 2 \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    main:app
