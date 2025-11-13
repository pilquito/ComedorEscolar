# 🚀 Despliegue en Dockploy - Guía Completa

Esta guía detalla cómo desplegar el Sistema de Gestión de Comedor Escolar en Dockploy.

## 📋 Preparación

### 1. Archivos Necesarios

Asegúrate de tener todos estos archivos en tu repositorio:

```
📦 proyecto/
├── 📄 Dockerfile
├── 📄 docker-compose.yml
├── 📄 docker-requirements.txt
├── 📄 .dockerignore
├── 📄 .env.example
├── 📄 start.sh
├── 📄 app.py
├── 📄 database.py
├── 📄 routes.py
├── 📄 models.py
├── 📄 main.py
├── 📁 templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── class_detail.html
│   ├── confirmados.html
│   ├── ausentes.html
│   ├── pendientes.html
│   ├── students.html
│   ├── teachers.html
│   └── classes.html
└── 📁 static/
    └── css/
        └── styles.css
```

### 2. Generar SESSION_SECRET

**IMPORTANTE:** Antes de desplegar, genera una clave secreta única:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Guarda este valor, lo necesitarás para configurar las variables de entorno.

## 🎯 Método 1: Despliegue via Docker Compose (Recomendado)

### Paso 1: Crear Servicio en Dockploy

1. Accede a tu panel de Dockploy
2. Click en **"New Service"** o **"Nuevo Servicio"**
3. Selecciona **"Docker Compose"**

### Paso 2: Configurar Docker Compose

Copia el contenido completo de `docker-compose.yml` en el editor de Dockploy.

### Paso 3: Variables de Entorno

Añade estas variables de entorno en Dockploy:

```env
SESSION_SECRET=tu-clave-generada-de-64-caracteres-aqui
FLASK_ENV=production
DATABASE_PATH=/app/data/cafeteria.db
TZ=Europe/Madrid
WORKERS=4
TIMEOUT=120
PORT=5000
```

### Paso 4: Configurar Volúmenes Persistentes

En Dockploy, asegúrate de que el volumen `cafeteria-data` está configurado como persistente.

### Paso 5: Desplegar

1. Click en **"Deploy"** o **"Desplegar"**
2. Espera a que el contenedor se construya e inicie
3. Verifica que el estado sea "Running"

### Paso 6: Configurar Dominio (Opcional)

1. En la configuración del servicio, añade tu dominio
2. Dockploy configurará automáticamente HTTPS con Let's Encrypt

## 🔧 Método 2: Despliegue via Dockerfile

### Paso 1: Crear Servicio

1. En Dockploy, selecciona **"Dockerfile"**
2. Conecta tu repositorio Git o sube los archivos

### Paso 2: Configuración Build

```
Build Context: .
Dockerfile Path: ./Dockerfile
```

### Paso 3: Variables de Entorno

Mismas que en Método 1 (ver arriba).

### Paso 4: Puerto

```
Puerto Interno: 5000
Puerto Externo: 80 (o el que prefieras)
```

### Paso 5: Volúmenes

Crear volumen persistente:
```
/app/data → volumen persistente para base de datos
```

## ✅ Verificación Post-Despliegue

### 1. Verificar Estado del Contenedor

```bash
docker ps | grep cafeteria
```

Deberías ver el contenedor con status "Up" y healthy.

### 2. Verificar Logs

En Dockploy:
- Ve a la sección de Logs
- Deberías ver: "Iniciando servidor con Gunicorn..."
- No debe haber errores rojos

### 3. Acceder a la Aplicación

Visita: `http://tu-dominio.com` o `http://tu-ip:5000`

Deberías ver la página de login.

### 4. Crear Primer Usuario

1. Importa un archivo CSV con datos iniciales, o
2. Accede a la gestión de profesores para crear el primer usuario

## 🔐 Configuración de Seguridad

### Variables de Entorno Obligatorias

```bash
SESSION_SECRET=<clave-aleatoria-64-caracteres>  # ¡OBLIGATORIO!
```

### Variables Recomendadas

```bash
FLASK_ENV=production
TZ=Europe/Madrid
WORKERS=4
TIMEOUT=120
```

### Permisos del Volumen

Dockploy gestiona automáticamente los permisos, pero puedes verificar:

```bash
docker exec <container-id> ls -la /app/data
```

## 📊 Monitoreo

### Healthcheck

El contenedor incluye healthcheck. En Dockploy verás:
- 🟢 Verde = Saludable
- 🔴 Rojo = Problema

### Logs en Tiempo Real

En Dockploy:
1. Selecciona tu servicio
2. Click en "Logs" o "Registros"
3. Activa "Live logs" para ver en tiempo real

### Métricas de Recursos

Dockploy muestra:
- Uso de CPU
- Uso de RAM
- Uso de disco
- Tráfico de red

## 🔄 Actualización de la Aplicación

### Método Automático (Git)

Si conectaste un repositorio:
1. Haz push de los cambios a tu repo
2. En Dockploy, click en "Redeploy"
3. Espera la reconstrucción

### Método Manual

1. Sube nuevos archivos a Dockploy
2. Click en "Rebuild"
3. Verifica que no haya errores en los logs

## 🆘 Solución de Problemas

### Contenedor no inicia

**Síntomas:** Estado "Exited" o "Error"

**Solución:**
1. Revisa logs en Dockploy
2. Verifica que SESSION_SECRET esté configurado
3. Comprueba que el puerto 5000 esté disponible

### Error de base de datos

**Síntomas:** "Database is locked" o errores de SQLite

**Solución:**
```bash
# Reiniciar contenedor
En Dockploy: Click en "Restart"
```

### Pérdida de datos tras reinicio

**Síntomas:** Los datos desaparecen al reiniciar

**Solución:**
1. Verifica que el volumen `/app/data` esté configurado como persistente
2. En Dockploy, ve a Volumes y confirma que existe `cafeteria-data`

### Puerto ya en uso

**Síntomas:** "Address already in use"

**Solución:**
- Cambia el puerto externo en Dockploy
- O detén el servicio que está usando el puerto 5000

### Variables de entorno no se aplican

**Solución:**
1. Verifica que las variables estén en la sección correcta de Dockploy
2. Después de cambiar variables, haz "Restart" del contenedor

## 📦 Backup y Restauración

### Crear Backup

**Opción 1: Via Dockploy**
1. Ve a Volumes
2. Busca `cafeteria-data`
3. Click en "Backup"

**Opción 2: Via Docker**
```bash
docker cp <container-name>:/app/data/cafeteria.db ./backup-$(date +%Y%m%d).db
```

### Restaurar Backup

```bash
docker cp ./backup.db <container-name>:/app/data/cafeteria.db
docker restart <container-name>
```

## 🌐 Configuración HTTPS

Dockploy configura automáticamente HTTPS si:
1. Tienes un dominio configurado
2. El dominio apunta a tu servidor
3. El puerto 80 y 443 están abiertos

No necesitas configurar certificados manualmente.

## 📈 Escalado

### Aumentar Workers

1. En variables de entorno, cambia:
   ```
   WORKERS=8
   ```
2. Reinicia el contenedor

**Recomendación:** `WORKERS = (2 × núcleos_CPU) + 1`

### Límites de Recursos

En Dockploy puedes configurar:
- **CPU:** 0.5 - 2.0 cores
- **RAM:** 512MB - 2GB
- **Disco:** 5GB - 20GB

## 🎓 Mejores Prácticas

1. **Siempre usa SESSION_SECRET aleatorio** único por instalación
2. **Backups automáticos** configurados en Dockploy
3. **Monitoreo activo** de logs y métricas
4. **Actualizaciones regulares** del código
5. **Variables de entorno** nunca en el código

## 📞 Soporte

Si tienes problemas:

1. **Revisa logs** primero
2. **Verifica variables de entorno**
3. **Comprueba el healthcheck**
4. **Revisa la documentación de Dockploy**

## ✨ Características Disponibles

Una vez desplegado, el sistema incluye:

- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión de estudiantes, clases y profesores
- ✅ Control de asistencia diaria al comedor
- ✅ Importación/Exportación CSV (formato PARTEGEN)
- ✅ Validación de comensales
- ✅ Reportes de confirmados, ausentes y pendientes
- ✅ Autenticación segura de profesores
- ✅ Interfaz responsive (móvil y desktop)

## 🎉 ¡Despliegue Exitoso!

Tu sistema de gestión de comedor está listo para usar. Accede a tu dominio y comienza a gestionar la asistencia de tus estudiantes.
