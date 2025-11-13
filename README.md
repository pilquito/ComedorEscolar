# 🍽️ Sistema de Gestión de Comedor Escolar

Sistema completo de gestión de asistencia diaria al comedor escolar, desarrollado en Flask con interfaz responsive y soporte para importación/exportación en formato PARTEGEN.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Características

### Gestión de Datos
- ✅ **Gestión de Estudiantes** - CRUD completo con validación
- ✅ **Gestión de Clases** - Organización por grupos
- ✅ **Gestión de Profesores** - Control de acceso y permisos
- ✅ **Control de Asistencia Diaria** - Registro en tiempo real

### Control de Comensales
- ✅ **Tipos de Comensales**
  - FIJO (continuo)
  - FIJO_DISCONTINUO (días específicos)
  - EXTRA (ocasional)
- ✅ **Validación de Asistencia** - Sistema de confirmación presente/ausente
- ✅ **Validación en Bloque** - Validar clase completa con un clic
- ✅ **Desbloqueo de Validación** - Modificar registros ya validados

### Importación/Exportación
- ✅ **Formato PARTEGEN** - Compatible con formato estándar
- ✅ **Formato PARTEI4A** - Soporte para archivos por clase
- ✅ **Exportación Idéntica** - Mantiene formato original exacto
- ✅ **Validación 100%** - Exportación solo con datos validados

### Dashboard y Reportes
- ✅ **Dashboard en Tiempo Real** - Estadísticas actualizadas
- ✅ **Reportes de Confirmados** - Lista de presentes
- ✅ **Reportes de Ausentes** - Control de faltas
- ✅ **Reportes de Pendientes** - Alumnos sin validar
- ✅ **Estadísticas por Clase** - Métricas detalladas

### Seguridad
- ✅ **Autenticación de Profesores** - Sistema de login seguro
- ✅ **Sesiones Cifradas** - Manejo seguro de sesiones
- ✅ **Asignación de Clases** - Permisos por profesor
- ✅ **Validación de Datos** - Integridad garantizada

### Interfaz
- ✅ **Diseño Responsive** - Compatible móvil y desktop
- ✅ **Modo Oscuro** - Interfaz moderna con Bootstrap
- ✅ **Notificaciones Toast** - Feedback visual inmediato
- ✅ **Iconos Font Awesome** - Interfaz intuitiva

## 🚀 Instalación Rápida

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/ComedorEscolar.git
cd ComedorEscolar

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar SESSION_SECRET

# 3. Iniciar con Docker Compose
docker-compose up -d

# 4. Acceder
# http://localhost:5000
```

**Ver:** [`DOCKER-QUICKSTART.md`](DOCKER-QUICKSTART.md) para guía completa.

### Opción 2: Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/ComedorEscolar.git
cd ComedorEscolar

# 2. Instalar dependencias
pip install -r docker-requirements.txt

# 3. Configurar variables de entorno
export SESSION_SECRET="tu-clave-secreta-aqui"
export FLASK_ENV="development"

# 4. Iniciar aplicación
python main.py

# 5. Acceder
# http://localhost:5000
```

## 📦 Despliegue en Producción

### Dockploy / Coolify / Portainer

Ver guía completa: [`DOCKPLOY-DEPLOYMENT.md`](DOCKPLOY-DEPLOYMENT.md)

**Pasos rápidos:**
1. Crear servicio Docker Compose
2. Pegar contenido de `docker-compose.yml`
3. Configurar `SESSION_SECRET` en variables de entorno
4. Deploy

### VPS / Servidor Dedicado

Ver guía completa: [`README-DOCKER.md`](README-DOCKER.md)

## 🔧 Configuración

### Variables de Entorno

#### Obligatorias
```bash
SESSION_SECRET=<clave-aleatoria-64-caracteres>
```

#### Opcionales
```bash
FLASK_ENV=production              # development o production
DATABASE_PATH=/app/data/cafeteria.db  # Ruta de base de datos
TZ=Europe/Madrid                  # Zona horaria
WORKERS=4                         # Workers de Gunicorn
TIMEOUT=120                       # Timeout en segundos
PORT=5000                         # Puerto de la aplicación
```

**Generar SESSION_SECRET:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 📖 Uso

### 1. Primer Inicio

1. **Acceder a la aplicación** - `http://localhost:5000`
2. **Importar datos iniciales** - Subir archivo CSV PARTEGEN
3. **Crear profesor** - Desde gestión de profesores
4. **Iniciar sesión** - Login con credenciales

### 2. Flujo Diario

1. **Login** - Ingresar con usuario profesor
2. **Dashboard** - Ver resumen del día
3. **Seleccionar Clase** - Click en "Ver Detalle"
4. **Marcar Asistencia** - Toggle "Viene Hoy" para cada alumno
5. **Validar** - Confirmar presentes/ausentes
6. **Exportar** - Descargar CSV cuando 100% validado

### 3. Importación CSV

**Formato PARTEGEN:**
```csv
FECHA;CURSO;CODIGO;NOMBRE DEL ALUMNO;FAL;COM;EXT
040925;INF4 A;12345;GARCÍA LÓPEZ, MARÍA;;C;
040925;INF4 A;12346;MARTÍNEZ RUIZ, JUAN;;D;
040925;INF4 A;12347;LÓPEZ SÁNCHEZ, ANA;;;E
```

**Columnas:**
- `FECHA` - Formato DDMMYY (ej: 040925 = 04/09/2025)
- `CURSO` - Código de clase
- `CODIGO` - ID del estudiante
- `NOMBRE DEL ALUMNO` - Formato: APELLIDOS NOMBRE
- `FAL` - Ausente ("F") o vacío
- `COM` - "C" (continuo), "D" (discontinuo) o vacío
- `EXT` - "E" (extra) o vacío

### 4. Exportación

- **CSV Estándar** - Para análisis en Excel
- **Formato Original** - Idéntico al importado (requiere 100% validado)

## 🏗️ Arquitectura

### Backend
- **Framework:** Flask 3.0
- **Base de Datos:** SQLite (migrable a PostgreSQL)
- **ORM:** SQL directo con dataclasses
- **Servidor:** Gunicorn (producción)

### Frontend
- **Template Engine:** Jinja2
- **CSS Framework:** Bootstrap 5 (tema oscuro)
- **Iconos:** Font Awesome 6
- **JavaScript:** Vanilla JS + Fetch API

### Estructura del Proyecto
```
ComedorEscolar/
├── app.py              # Configuración Flask
├── database.py         # Lógica de base de datos
├── routes.py           # Rutas y endpoints
├── models.py           # Modelos de datos
├── main.py            # Punto de entrada
├── templates/         # Plantillas HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── class_detail.html
│   ├── confirmados.html
│   ├── ausentes.html
│   ├── pendientes.html
│   ├── students.html
│   ├── teachers.html
│   └── classes.html
├── static/            # Archivos estáticos
│   └── css/
│       └── styles.css
├── Dockerfile         # Imagen Docker
├── docker-compose.yml # Orquestación
├── start.sh          # Script de inicio
└── README.md         # Este archivo
```

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Sesiones cifradas con SECRET_KEY
- ✅ Protección CSRF
- ✅ SQL injection prevention (consultas parametrizadas)
- ✅ Validación de entrada de datos
- ✅ Headers de seguridad con ProxyFix

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest tests/

# Verificar base de datos
python -c "from database import verify_database_integrity; verify_database_integrity()"
```

## 📊 Requisitos del Sistema

### Mínimos
- CPU: 0.5 cores
- RAM: 512 MB
- Disco: 2 GB
- Python: 3.11+

### Recomendados
- CPU: 1-2 cores
- RAM: 1 GB
- Disco: 5 GB
- Python: 3.11+

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [`LICENSE`](LICENSE) para más detalles.

## 🆘 Soporte

- **Documentación:** Ver carpeta `docs/`
- **Issues:** GitHub Issues
- **Guías:**
  - [Docker Quickstart](DOCKER-QUICKSTART.md)
  - [Dockploy Deployment](DOCKPLOY-DEPLOYMENT.md)
  - [README Docker](README-DOCKER.md)
  - [Deployment Checklist](DEPLOYMENT-CHECKLIST.md)

## 🗺️ Roadmap

- [ ] Tests unitarios y de integración
- [ ] API REST completa
- [ ] Exportación a PDF
- [ ] Notificaciones por email
- [ ] Dashboard con gráficos
- [ ] Soporte multi-idioma
- [ ] Modo offline (PWA)
- [ ] Integración con sistemas escolares

## 👥 Autores

Desarrollado para la gestión eficiente de comedores escolares.

## 🙏 Agradecimientos

- Bootstrap Team por el framework CSS
- Font Awesome por los iconos
- Flask Team por el framework web
- Comunidad de código abierto

---

**Hecho con ❤️ para mejorar la gestión de comedores escolares**
