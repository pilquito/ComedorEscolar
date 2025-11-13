# 🚀 Despliegue Docker - Guía Rápida

## 📦 Todo Está Listo

El sistema está **100% empaquetado** y listo para Docker/Dockploy con:

✅ Dockerfile optimizado  
✅ Docker Compose configurado  
✅ Variables de entorno documentadas  
✅ Script de inicio automatizado  
✅ Base de datos con volumen persistente  
✅ Healthcheck incluido  
✅ Documentación completa  

## ⚡ Despliegue en 3 Pasos

### 1️⃣ Generar SESSION_SECRET

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Copia el resultado**, lo necesitarás en el paso 3.

### 2️⃣ Subir a Dockploy

**En Dockploy:**
1. New Service → Docker Compose
2. Pegar contenido de `docker-compose.yml`

### 3️⃣ Configurar Variables

**En la sección de Environment Variables de Dockploy:**

```env
SESSION_SECRET=pega-aqui-el-valor-generado-en-paso-1
FLASK_ENV=production
DATABASE_PATH=/app/data/cafeteria.db
TZ=Europe/Madrid
```

**Deploy** → ¡Listo!

## 🌐 Acceder

Después del despliegue:
- URL: `http://tu-dominio.com` o `http://tu-ip:5000`
- Verás la página de login
- Importa tu archivo CSV para comenzar

## 📁 Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `Dockerfile` | Imagen Docker |
| `docker-compose.yml` | Configuración de servicios |
| `.env.example` | Plantilla de variables |
| `start.sh` | Script de inicio |
| `README-DOCKER.md` | Documentación completa |
| `DOCKPLOY-DEPLOYMENT.md` | Guía Dockploy paso a paso |
| `DEPLOYMENT-CHECKLIST.md` | Lista de verificación |

## 🔧 Variables de Entorno

### Obligatorias
```
SESSION_SECRET    # Clave secreta única (64 caracteres)
```

### Opcionales (con valores por defecto)
```
FLASK_ENV=production
DATABASE_PATH=/app/data/cafeteria.db
TZ=Europe/Madrid
WORKERS=4
TIMEOUT=120
PORT=5000
```

## 💾 Base de Datos

- **Tipo:** SQLite (incluido, no requiere servidor externo)
- **Ubicación:** `/app/data/cafeteria.db` (volumen persistente)
- **Backup:** Automático con volumen Docker
- **Persistencia:** Los datos NO se pierden al reiniciar

## 📊 Recursos

**Mínimos:**
- CPU: 0.5 cores
- RAM: 512 MB
- Disco: 2 GB

**Recomendados:**
- CPU: 1 core
- RAM: 1 GB
- Disco: 5 GB

## ✅ Verificación

Después del despliegue, verifica:

1. **Estado:** Contenedor "running" con healthcheck ✅
2. **Logs:** Sin errores rojos
3. **Acceso:** `http://tu-dominio:5000` carga página de login
4. **Persistencia:** Importa datos CSV, reinicia, datos persisten

## 🆘 Problemas Comunes

### Contenedor no inicia
**Causa:** Falta SESSION_SECRET  
**Solución:** Añadir variable de entorno

### Datos se pierden
**Causa:** Volumen no persistente  
**Solución:** Verificar que `cafeteria-data` es volumen persistente

### Puerto ocupado
**Causa:** Puerto 5000 ya en uso  
**Solución:** Cambiar puerto externo en Dockploy

## 📚 Más Información

- **Docker local:** Ver `README-DOCKER.md`
- **Dockploy:** Ver `DOCKPLOY-DEPLOYMENT.md`
- **Checklist:** Ver `DEPLOYMENT-CHECKLIST.md`

## 🎯 Comando de Prueba Local

```bash
# Prueba rápida en local
docker-compose up -d
docker-compose logs -f
```

## ✨ Características Incluidas

- 📊 Dashboard con estadísticas
- 👥 Gestión de estudiantes y profesores
- 📝 Control de asistencia diaria
- 📤 Importación/Exportación CSV (PARTEGEN)
- ✅ Validación de comensales
- 📋 Reportes completos
- 🔐 Autenticación segura
- 📱 Interfaz responsive

## 🎉 ¡Todo Listo!

Tu sistema está empaquetado y listo para producción.

**Siguiente paso:** Generar SESSION_SECRET y desplegar en Dockploy.

---

**Nota:** Todos los archivos Docker necesarios están en el directorio raíz del proyecto.
