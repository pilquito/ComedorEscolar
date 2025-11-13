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

# Inicializar base de datos si no existe
if [ ! -f "${DATABASE_PATH:-/app/data/cafeteria.db}" ]; then
    echo "🗄️  Base de datos no encontrada. Inicializando..."
    python -c "from database import init_db; init_db()"
    echo "✅ Base de datos inicializada"
else
    echo "✅ Base de datos existente encontrada"
fi

# Verificar integridad de la base de datos
echo "🔍 Verificando integridad de la base de datos..."
python -c "from database import verify_database_integrity; verify_database_integrity()"

echo ""
echo "========================================="
echo "🚀 Iniciando servidor con Gunicorn..."
echo "========================================="
echo ""

# Ejecutar Gunicorn con configuración
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${WORKERS:-4} \
    --threads 2 \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    main:app
