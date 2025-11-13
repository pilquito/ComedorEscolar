#!/bin/bash
# Script para publicar rápidamente en GitHub
# Uso: ./publish-github.sh TU-USUARIO

set -e

echo "========================================="
echo "🚀 Publicación en GitHub"
echo "Sistema de Gestión de Comedor Escolar"
echo "========================================="
echo ""

# Verificar parámetro
if [ -z "$1" ]; then
    echo "❌ Error: Falta nombre de usuario de GitHub"
    echo ""
    echo "Uso: ./publish-github.sh TU-USUARIO"
    echo "Ejemplo: ./publish-github.sh johndoe"
    echo ""
    exit 1
fi

GITHUB_USER=$1
REPO_URL="https://github.com/$GITHUB_USER/ComedorEscolar.git"

echo "📋 Configuración:"
echo "   Usuario: $GITHUB_USER"
echo "   Repositorio: $REPO_URL"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "README.md" ]; then
    echo "❌ Error: Este script debe ejecutarse desde la carpeta ComedorEscolar"
    exit 1
fi

# Verificar que no hay .env o .db
if [ -f ".env" ] || [ -f "cafeteria.db" ]; then
    echo "⚠️  ADVERTENCIA: Encontrados archivos sensibles (.env o cafeteria.db)"
    echo "   Estos archivos están en .gitignore y NO se subirán"
    echo ""
fi

# Inicializar repositorio si no existe
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositorio Git..."
    git init
    echo "✅ Repositorio inicializado"
else
    echo "✅ Repositorio Git ya existe"
fi

# Añadir todos los archivos
echo ""
echo "📦 Añadiendo archivos..."
git add .
echo "✅ Archivos añadidos"

# Crear commit
echo ""
echo "💾 Creando commit inicial..."
git commit -m "feat: versión inicial del sistema de gestión de comedor escolar

- Sistema completo de gestión de estudiantes, profesores y clases
- Control de asistencia diaria con validación
- Importación/Exportación formato PARTEGEN
- Dashboard con estadísticas en tiempo real
- Docker ready para producción
- Documentación completa

Ver CHANGELOG.md para detalles completos." || echo "ℹ️  Sin cambios para commit"

echo "✅ Commit creado"

# Configurar rama main
echo ""
echo "🌿 Configurando rama main..."
git branch -M main
echo "✅ Rama configurada"

# Añadir repositorio remoto
echo ""
echo "🔗 Configurando repositorio remoto..."
if git remote get-url origin > /dev/null 2>&1; then
    echo "ℹ️  Remote 'origin' ya existe, actualizando URL..."
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi
echo "✅ Remote configurado: $REPO_URL"

# Mostrar información
echo ""
echo "========================================="
echo "✅ Repositorio local listo"
echo "========================================="
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Crear repositorio en GitHub:"
echo "   https://github.com/new"
echo "   - Repository name: ComedorEscolar"
echo "   - NO inicializar con README/LICENSE/.gitignore"
echo ""
echo "2. Cuando el repositorio esté creado en GitHub, ejecuta:"
echo "   git push -u origin main"
echo ""
echo "3. Verificar en:"
echo "   $REPO_URL"
echo ""
echo "========================================="
echo ""

# Preguntar si quiere hacer push ahora
read -p "¿Quieres hacer push ahora? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Publicando en GitHub..."
    echo ""
    git push -u origin main
    echo ""
    echo "========================================="
    echo "✅ ¡Publicación exitosa!"
    echo "========================================="
    echo ""
    echo "Tu proyecto está disponible en:"
    echo "$REPO_URL"
    echo ""
    echo "Próximos pasos sugeridos:"
    echo "- Añadir topics al repositorio"
    echo "- Crear un release (v1.0.0)"
    echo "- Invitar colaboradores"
    echo "- Configurar GitHub Actions"
    echo ""
else
    echo ""
    echo "ℹ️  Push cancelado"
    echo "Cuando estés listo, ejecuta: git push -u origin main"
    echo ""
fi

echo "========================================="
echo "📚 Documentación disponible:"
echo "   - GITHUB-SETUP.md (guía completa)"
echo "   - README.md (documentación principal)"
echo "   - CONTRIBUTING.md (guía de contribución)"
echo "========================================="
