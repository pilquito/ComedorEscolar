# 📤 Publicar en GitHub - Guía Paso a Paso

## 🎯 Objetivo

Publicar el Sistema de Gestión de Comedor Escolar en tu repositorio de GitHub.

## 📋 Pre-requisitos

- Cuenta de GitHub
- Git instalado en tu sistema
- Todos los archivos del proyecto en la carpeta `ComedorEscolar`

## 🚀 Pasos para Publicar

### 1. Crear Repositorio en GitHub

1. Ve a [GitHub](https://github.com)
2. Click en el botón **"New"** o **"+"** → **"New repository"**
3. Configurar repositorio:
   - **Repository name:** `ComedorEscolar`
   - **Description:** `Sistema de gestión de asistencia diaria al comedor escolar`
   - **Visibility:** Public o Private (tu elección)
   - **NO** inicializar con README, .gitignore o license (ya los tienes)
4. Click en **"Create repository"**

### 2. Configurar Git Localmente

Abre terminal en la carpeta `ComedorEscolar`:

```bash
# Navegar a la carpeta
cd ComedorEscolar

# Inicializar repositorio Git
git init

# Configurar tu información (si aún no lo hiciste)
git config user.name "Tu Nombre"
git config user.email "tu-email@example.com"
```

### 3. Añadir Archivos

```bash
# Ver estado de archivos
git status

# Añadir todos los archivos
git add .

# Verificar qué se añadió
git status

# Crear commit inicial
git commit -m "feat: versión inicial del sistema de gestión de comedor escolar

- Sistema completo de gestión de estudiantes, profesores y clases
- Control de asistencia diaria con validación
- Importación/Exportación formato PARTEGEN
- Dashboard con estadísticas en tiempo real
- Docker ready para producción
- Documentación completa"
```

### 4. Conectar con GitHub

Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub:

```bash
# Añadir repositorio remoto
git remote add origin https://github.com/TU-USUARIO/ComedorEscolar.git

# Verificar que se añadió correctamente
git remote -v
```

### 5. Publicar

```bash
# Push al repositorio (primera vez)
git push -u origin main

# Si pide crear rama 'main'
git branch -M main
git push -u origin main
```

### 6. Verificar en GitHub

1. Ve a `https://github.com/TU-USUARIO/ComedorEscolar`
2. Deberías ver todos los archivos
3. El README.md se mostrará automáticamente

## 🏷️ Crear Release (Opcional pero Recomendado)

### Via Web (Más Fácil)

1. En tu repositorio de GitHub, click en **"Releases"**
2. Click en **"Create a new release"**
3. Configurar:
   - **Tag version:** `v1.0.0`
   - **Release title:** `v1.0.0 - Primera Versión Estable`
   - **Description:** Copiar contenido de CHANGELOG.md
4. Click en **"Publish release"**

### Via Comandos

```bash
# Crear tag
git tag -a v1.0.0 -m "v1.0.0 - Primera versión estable"

# Push tag
git push origin v1.0.0
```

## 📝 Actualizar Repositorio

Para futuras actualizaciones:

```bash
# Ver cambios
git status

# Añadir archivos modificados
git add .

# Commit con mensaje descriptivo
git commit -m "fix: corregir bug en exportación CSV"

# Push
git push
```

## 🔧 Configurar GitHub Pages (Opcional)

Si quieres alojar la documentación en GitHub Pages:

1. En tu repositorio, ve a **Settings** → **Pages**
2. En **Source**, selecciona **"main"** branch
3. En folder, selecciona **"/ (root)"**
4. Click en **Save**
5. Tu documentación estará en: `https://TU-USUARIO.github.io/ComedorEscolar`

## 🏷️ Topics Recomendados

Añade estos topics a tu repositorio para mejor visibilidad:

```
python
flask
school-management
cafeteria
attendance-system
docker
bootstrap
sqlite
education
spanish
```

Para añadirlos:
1. En tu repositorio de GitHub
2. Click en ⚙️ junto a **"About"**
3. Añadir topics en el campo correspondiente
4. Guardar cambios

## 📊 GitHub Actions (CI/CD) - Opcional

Crear archivo `.github/workflows/docker-image.yml`:

```yaml
name: Docker Image CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build . --file Dockerfile --tag comedorescolar:$(date +%s)
    
    - name: Test Docker image
      run: docker run -d -p 5000:5000 -e SESSION_SECRET=test comedorescolar:latest
```

## 🔒 Proteger Secrets

**IMPORTANTE:** Nunca subas:
- Archivos `.env` con datos reales
- Base de datos `cafeteria.db` con datos sensibles
- SESSION_SECRET real

El `.gitignore` ya está configurado para ignorarlos.

## 📋 Checklist Final

Antes de publicar, verificar:

- [ ] README.md actualizado con URL correcta
- [ ] LICENSE incluido
- [ ] .gitignore configurado
- [ ] No hay archivos sensibles (`.env`, `*.db`)
- [ ] Documentación completa
- [ ] Tests pasan (si existen)
- [ ] Docker build funciona
- [ ] Links en README apuntan correctamente

## 🆘 Problemas Comunes

### "Permission denied (publickey)"

**Solución:** Configurar SSH keys o usar HTTPS:
```bash
git remote set-url origin https://github.com/TU-USUARIO/ComedorEscolar.git
```

### "Updates were rejected"

**Solución:** Pull primero:
```bash
git pull origin main --rebase
git push
```

### Archivo muy grande

**Solución:** Añadir a .gitignore y commit de nuevo:
```bash
echo "archivo-grande.db" >> .gitignore
git rm --cached archivo-grande.db
git commit -m "remove large file"
git push
```

## 📞 Recursos

- [GitHub Docs](https://docs.github.com)
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Markdown Guide](https://www.markdownguide.org/)

## ✅ Verificación Post-Publicación

1. **Clonar en otro directorio** para probar:
   ```bash
   cd /tmp
   git clone https://github.com/TU-USUARIO/ComedorEscolar.git
   cd ComedorEscolar
   docker-compose up -d
   ```

2. **Verificar que funciona:**
   - Acceder a `http://localhost:5000`
   - Importar CSV de prueba
   - Validar funcionalidad básica

## 🎉 ¡Listo!

Tu proyecto está publicado y accesible en GitHub.

**URL del repositorio:** `https://github.com/TU-USUARIO/ComedorEscolar`

---

**Próximos pasos sugeridos:**
1. Compartir URL con colaboradores
2. Configurar GitHub Actions
3. Añadir badges al README
4. Crear issues para mejoras futuras
5. Invitar colaboradores
