# 🐳 Sistema de Gestión de Comedor Escolar - Docker

Sistema completo de gestión de comedor escolar empaquetado para Docker y Dockploy.

## 📋 Requisitos Previos

- Docker Engine 20.10+
- Docker Compose 2.0+
- 1GB RAM mínimo
- 500MB espacio en disco

## 🚀 Instalación Rápida

### 1. Clonar o copiar archivos del proyecto

```bash
# Asegúrate de tener todos estos archivos:
# - Dockerfile
# - docker-compose.yml
# - .env.example
# - docker-requirements.txt
# - app.py, database.py, routes.py, models.py, main.py
# - templates/ (directorio completo)
# - static/ (directorio completo)
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y cambiar SESSION_SECRET
nano .env
```

**IMPORTANTE:** Generar SESSION_SECRET aleatorio:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Construir y ejecutar

```bash
# Construir la imagen
docker-compose build

# Iniciar la aplicación
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4. Acceder a la aplicación

Abrir navegador en: `http://localhost:5000`

**Usuario por defecto:** (se crea en el primer inicio)
- Crear usuario desde la interfaz de gestión

## 🔧 Comandos Útiles

### Gestión del contenedor

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# Ver estado
docker-compose ps
```

### Base de datos

```bash
# Hacer backup de la base de datos
docker cp cafeteria-management:/app/data/cafeteria.db ./backup-$(date +%Y%m%d).db

# Restaurar backup
docker cp ./backup-20240101.db cafeteria-management:/app/data/cafeteria.db
docker-compose restart
```

### Mantenimiento

```bash
# Limpiar contenedores parados
docker-compose down --volumes

# Reconstruir desde cero
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up -d
```

## 📦 Despliegue en Dockploy

### Opción 1: Via Docker Compose

1. **Crear nuevo servicio en Dockploy**
2. **Seleccionar "Docker Compose"**
3. **Copiar contenido de `docker-compose.yml`**
4. **Configurar variables de entorno:**
   ```
   SESSION_SECRET=tu-clave-secreta-aleatoria-aqui
   FLASK_ENV=production
   TZ=Europe/Madrid
   ```
5. **Desplegar**

### Opción 2: Via Dockerfile

1. **Crear nuevo servicio en Dockploy**
2. **Seleccionar "Dockerfile"**
3. **Conectar repositorio o subir código**
4. **Configurar variables de entorno** (ver .env.example)
5. **Puerto:** 5000
6. **Desplegar**

## 🔐 Configuración de Seguridad

### Variables de Entorno Obligatorias

```bash
SESSION_SECRET=<generar-clave-aleatoria-64-caracteres>
```

### Variables Opcionales

```bash
FLASK_ENV=production
TZ=Europe/Madrid
WORKERS=4
TIMEOUT=120
```

## 📂 Estructura de Volúmenes

```
cafeteria-data/         # Base de datos SQLite persistente
  └── cafeteria.db      # Archivo principal de base de datos

logs/                   # Logs de aplicación (opcional)
  ├── access.log
  └── error.log
```

## 🔍 Troubleshooting

### La aplicación no inicia

```bash
# Ver logs detallados
docker-compose logs cafeteria-app

# Verificar que el puerto 5000 no está en uso
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows
```

### Pérdida de datos

```bash
# Verificar que el volumen existe
docker volume ls | grep cafeteria

# Inspeccionar volumen
docker volume inspect cafeteria_cafeteria-data
```

### Problemas de permisos

```bash
# Dar permisos al directorio de datos
docker exec cafeteria-management chown -R nobody:nogroup /app/data
```

### Error de base de datos

```bash
# Reinicializar base de datos (CUIDADO: borra todos los datos)
docker-compose down -v
docker-compose up -d
```

## 📊 Monitoreo

### Healthcheck

El contenedor incluye healthcheck automático:
- Intervalo: 30 segundos
- Timeout: 10 segundos
- Reintentos: 3

```bash
# Ver estado de salud
docker inspect cafeteria-management | grep -A 10 Health
```

### Recursos

```bash
# Ver uso de recursos
docker stats cafeteria-management
```

## 🔄 Actualización

```bash
# 1. Hacer backup
docker cp cafeteria-management:/app/data/cafeteria.db ./backup.db

# 2. Detener contenedor
docker-compose down

# 3. Actualizar código
git pull  # o copiar nuevos archivos

# 4. Reconstruir
docker-compose build

# 5. Iniciar
docker-compose up -d
```

## 🌐 Configuración de Proxy Reverso (Nginx)

```nginx
server {
    listen 80;
    server_name comedor.tuescuela.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📝 Características del Sistema

- ✅ Gestión de estudiantes y clases
- ✅ Control de asistencia diaria
- ✅ Tipos de comensales (FIJO, DISCONTINUO, EXTRA)
- ✅ Validación de asistencia
- ✅ Importación/Exportación CSV (formato PARTEGEN)
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Autenticación de profesores
- ✅ Reportes y exportaciones

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs: `docker-compose logs -f`
2. Verificar variables de entorno en `.env`
3. Comprobar que el puerto 5000 está disponible
4. Verificar permisos del volumen de datos

## 📄 Licencia

Sistema de Gestión de Comedor Escolar
Desarrollado para gestión educativa
