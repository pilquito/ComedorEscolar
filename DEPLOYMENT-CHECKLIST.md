# ✅ Lista de Verificación de Despliegue Docker

## 📦 Archivos Creados para Docker/Dockploy

### Archivos Docker Principales
- ✅ `Dockerfile` - Configuración de imagen Docker
- ✅ `docker-compose.yml` - Orquestación de servicios
- ✅ `docker-requirements.txt` - Dependencias Python para Docker
- ✅ `.dockerignore` - Archivos excluidos de la imagen
- ✅ `start.sh` - Script de inicio automatizado

### Configuración
- ✅ `.env.example` - Plantilla de variables de entorno
- ✅ `database.py` - Actualizado para soportar volúmenes Docker

### Documentación
- ✅ `README-DOCKER.md` - Guía completa de Docker
- ✅ `DOCKPLOY-DEPLOYMENT.md` - Guía específica para Dockploy
- ✅ `DEPLOYMENT-CHECKLIST.md` - Este archivo

## 🔧 Variables de Entorno Requeridas

### Obligatorias
```bash
SESSION_SECRET=<generar-con-python3 -c "import secrets; print(secrets.token_hex(32))">
```

### Recomendadas
```bash
FLASK_ENV=production
DATABASE_PATH=/app/data/cafeteria.db
TZ=Europe/Madrid
WORKERS=4
TIMEOUT=120
PORT=5000
```

## 🚀 Pasos Rápidos de Despliegue

### Opción A: Docker Compose Local

```bash
# 1. Copiar y configurar variables
cp .env.example .env
nano .env  # Editar SESSION_SECRET

# 2. Construir y ejecutar
docker-compose build
docker-compose up -d

# 3. Verificar
docker-compose ps
docker-compose logs -f
```

### Opción B: Dockploy

1. **Crear servicio** → Docker Compose
2. **Pegar** contenido de `docker-compose.yml`
3. **Configurar variables** (ver sección arriba)
4. **Deploy**

## 📋 Verificación Post-Despliegue

- [ ] Contenedor inicia correctamente
- [ ] Logs no muestran errores
- [ ] Healthcheck pasa (status: healthy)
- [ ] Aplicación accesible en puerto 5000
- [ ] Página de login carga correctamente
- [ ] Base de datos se crea en `/app/data/`
- [ ] Importación CSV funciona
- [ ] Datos persisten tras reiniciar contenedor

## 🗂️ Estructura de Volúmenes

```
cafeteria-data/          → /app/data (persistente)
  └── cafeteria.db       → Base de datos SQLite
  
logs/                    → /app/logs (opcional)
  ├── access.log
  └── error.log
```

## 🔒 Seguridad

- [ ] `SESSION_SECRET` único y aleatorio configurado
- [ ] `FLASK_ENV=production` en producción
- [ ] Volúmenes configurados como persistentes
- [ ] Puerto 5000 protegido con proxy reverso (Nginx)
- [ ] HTTPS configurado (Let's Encrypt via Dockploy)
- [ ] Backups automáticos configurados

## 📊 Recursos Recomendados

### Mínimos
- CPU: 0.5 cores
- RAM: 512 MB
- Disco: 2 GB

### Recomendados
- CPU: 1-2 cores
- RAM: 1 GB
- Disco: 5 GB

### Producción (>100 usuarios concurrentes)
- CPU: 2-4 cores
- RAM: 2 GB
- Disco: 10 GB

## 🔄 Comandos Útiles

### Docker Compose
```bash
docker-compose up -d              # Iniciar
docker-compose down               # Detener
docker-compose restart            # Reiniciar
docker-compose logs -f            # Ver logs
docker-compose ps                 # Estado
docker-compose build --no-cache   # Reconstruir
```

### Backup
```bash
# Crear backup
docker cp cafeteria-management:/app/data/cafeteria.db ./backup.db

# Restaurar backup
docker cp ./backup.db cafeteria-management:/app/data/cafeteria.db
docker-compose restart
```

## 🆘 Troubleshooting

### Problema: Contenedor no inicia
**Verificar:**
- [ ] SESSION_SECRET está configurado
- [ ] Puerto 5000 disponible
- [ ] Volumen tiene permisos correctos
- [ ] Logs: `docker-compose logs`

### Problema: Datos se pierden
**Verificar:**
- [ ] Volumen `cafeteria-data` es persistente
- [ ] DATABASE_PATH apunta a `/app/data/cafeteria.db`
- [ ] No usar `docker-compose down -v` (borra volúmenes)

### Problema: Error de base de datos
**Solución:**
```bash
docker-compose restart
# o
docker exec cafeteria-management python -c "from database import init_db; init_db()"
```

## 📞 Contacto y Soporte

Para más información:
- Ver `README-DOCKER.md` - Guía completa Docker
- Ver `DOCKPLOY-DEPLOYMENT.md` - Guía Dockploy
- Revisar logs: `docker-compose logs -f`

## ✨ Características del Sistema

- Dashboard con estadísticas en tiempo real
- Gestión de estudiantes, clases y profesores
- Control de asistencia diaria
- Importación/Exportación CSV (PARTEGEN)
- Validación de comensales
- Reportes (confirmados, ausentes, pendientes)
- Autenticación de profesores
- Interfaz responsive

## 🎉 ¡Listo para Producción!

Todos los archivos están configurados y listos para desplegar.

**Último paso antes de desplegar:**
```bash
# Generar SESSION_SECRET
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Guarda este valor y úsalo en las variables de entorno.

---

**Fecha de creación:** $(date)
**Versión:** 1.0.0
