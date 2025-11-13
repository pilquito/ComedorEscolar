# 🔧 Solución de Problemas - Dockploy

## Error: "No such container: select-a-container"

Este error indica que el contenedor no se creó correctamente. Aquí está la solución paso a paso.

## ✅ Solución Garantizada

### Opción 1: Despliegue Manual con Docker (Más Confiable)

Si Dockploy da problemas, puedes desplegar directamente en tu servidor:

```bash
# 1. Clonar el repositorio
git clone https://github.com/pilquito/ComedorEscolar.git
cd ComedorEscolar

# 2. Crear archivo .env con tus variables
cat > .env << EOF
SESSION_SECRET=7c2de8ea4fcbe030c88b042ee549c40fa291016c0657d8fc2a542cc98157621b
FLASK_ENV=production
DATABASE_PATH=/app/data/cafeteria.db
PORT=5000
WORKERS=4
TZ=Europe/Madrid
EOF

# 3. Construir y ejecutar con Docker Compose
docker-compose up -d

# 4. Verificar que está corriendo
docker-compose ps
docker-compose logs -f
```

### Opción 2: Configuración Correcta en Dockploy

#### Paso 1: Usar GitHub Deploy (no Docker Compose)

En Dockploy:
1. **New Service** → **GitHub**
2. Selecciona tu repositorio: `pilquito/ComedorEscolar`
3. Branch: `main`

#### Paso 2: Configuración de Build

```
Build Method: Dockerfile
Dockerfile Path: ./Dockerfile
Build Context: .
```

#### Paso 3: Variables de Entorno (cópialas exactamente)

```
SESSION_SECRET=7c2de8ea4fcbe030c88b042ee549c40fa291016c0657d8fc2a542cc98157621b
FLASK_ENV=production
DATABASE_PATH=/app/data/cafeteria.db
PORT=5000
WORKERS=4
TZ=Europe/Madrid
LANG=es_ES.UTF-8
```

#### Paso 4: Port Mapping

```
Container Port: 5000
Host Port: (el que te asigne Dockploy, generalmente 80 o 443)
```

#### Paso 5: Volumes (MUY IMPORTANTE)

```
/app/data → Persistent Volume (para la base de datos)
```

#### Paso 6: Health Check (opcional pero recomendado)

```
Health Check Path: /login
Health Check Interval: 30s
```

### Opción 3: Dockerfile Standalone (Más Simple)

Si Docker Compose falla, usa solo el Dockerfile:

```bash
# En tu servidor
git clone https://github.com/pilquito/ComedorEscolar.git
cd ComedorEscolar

# Build
docker build -t comedor-escolar .

# Run con variables de entorno
docker run -d \
  --name comedor-escolar \
  -p 5000:5000 \
  -v comedor-data:/app/data \
  -e SESSION_SECRET=7c2de8ea4fcbe030c88b042ee549c40fa291016c0657d8fc2a542cc98157621b \
  -e FLASK_ENV=production \
  -e DATABASE_PATH=/app/data/cafeteria.db \
  -e PORT=5000 \
  -e WORKERS=4 \
  -e TZ=Europe/Madrid \
  --restart unless-stopped \
  comedor-escolar

# Ver logs
docker logs -f comedor-escolar
```

## 🔍 Diagnóstico de Problemas

### Verificar si el build funciona

```bash
# Test local del build
docker build -t test-comedor .

# Si falla, verás el error exacto
# Si funciona, verás: "Successfully built..."
```

### Ver logs de construcción en Dockploy

1. Ve a tu servicio en Dockploy
2. Tab **"Logs"** o **"Build Logs"**
3. Busca errores en rojo
4. Copia el error completo

### Errores Comunes y Soluciones

#### Error: "failed to solve with frontend dockerfile.v0"
**Solución:** Problema con el Dockerfile. Usa la última versión de GitHub.

#### Error: "no space left on device"
**Solución:** Limpia imágenes viejas:
```bash
docker system prune -a
```

#### Error: "port already in use"
**Solución:** Cambia el puerto en variables de entorno:
```
PORT=5001
```

#### Error: "permission denied"
**Solución:** El usuario de Docker no tiene permisos:
```bash
sudo usermod -aG docker $USER
```

## 📊 Verificar que Funciona

Una vez desplegado, deberías poder:

```bash
# Verificar que el contenedor está corriendo
curl http://localhost:5000/login

# Deberías ver el HTML de la página de login
```

## 🆘 Si Nada Funciona

### Test Rápido Local

Para verificar que el proyecto funciona (en tu máquina local):

```bash
# Clonar
git clone https://github.com/pilquito/ComedorEscolar.git
cd ComedorEscolar

# Instalar dependencias
pip install -r requirements.txt

# Configurar variable
export SESSION_SECRET=7c2de8ea4fcbe030c88b042ee549c40fa291016c0657d8fc2a542cc98157621b

# Ejecutar con Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 main:app
```

Si esto funciona, el problema está en Dockploy, no en el código.

## 💡 Alternativas a Dockploy

Si Dockploy continúa dando problemas, puedes usar:

1. **Railway.app** - Deploy directo desde GitHub
2. **Render.com** - Gratis con Docker
3. **Fly.io** - Deploy global con Docker
4. **DigitalOcean App Platform** - Muy fácil
5. **Docker directo en VPS** - Máximo control

## 📞 Información para Soporte

Si contactas a soporte de Dockploy, proporciona:

```
- Repository: https://github.com/pilquito/ComedorEscolar
- Error: "No such container: select-a-container"
- Build Method: Dockerfile / Docker Compose
- Dockerfile Path: ./Dockerfile
- Port: 5000
```

## ✅ Checklist Final

- [ ] Repository conectado correctamente
- [ ] Variables de entorno configuradas (especialmente SESSION_SECRET)
- [ ] Puerto 5000 mapeado
- [ ] Volumen persistente para /app/data
- [ ] Build logs sin errores rojos
- [ ] Contenedor muestra estado "Running"
- [ ] Health check pasa (si configurado)

---

**Última actualización:** 2025-11-13
