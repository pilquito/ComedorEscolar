# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2024-11-13

### ✨ Añadido

#### Gestión de Datos
- Sistema completo de gestión de estudiantes (CRUD)
- Sistema completo de gestión de profesores (CRUD)
- Sistema completo de gestión de clases
- Base de datos SQLite con soporte para volúmenes Docker

#### Control de Comensales
- Tipos de comensales: FIJO, FIJO_DISCONTINUO, EXTRA
- Control de asistencia diaria ("Viene Hoy")
- Sistema de validación individual de estudiantes
- Validación en bloque de clase completa
- Sistema de desbloqueo de validación
- Marcado automático de ausentes al cambiar "Viene Hoy"

#### Dashboard y Reportes
- Dashboard con estadísticas en tiempo real
- Tarjetas de resumen (Total, Comen Hoy, Confirmados, Ausentes, Sin Validar, % Validado)
- Vista de clases con estadísticas individuales
- Página de comensales confirmados (presentes)
- Página de comensales ausentes
- Página de comensales pendientes de validar
- Enlaces clickeables en estadísticas

#### Importación/Exportación
- Importación CSV formato PARTEGEN (FECHA;CURSO;CODIGO;NOMBRE;FAL;COM;EXT)
- Importación CSV formato PARTEI4A (por clase individual)
- Exportación formato original PARTEGEN (idéntico al importado)
- Exportación CSV estándar para análisis
- Validación de formato DDMMYY en fechas
- Soporte para nombres "APELLIDOS NOMBRE" (sin coma)
- Valores en mayúsculas: COM (C/D), EXT (E), FAL (F)
- Nombre de archivo exportado: PARTGEN.csv (sin fecha)
- Exportación solo permitida cuando 100% validado

#### Autenticación y Seguridad
- Sistema de login para profesores
- Sesiones cifradas con SESSION_SECRET
- Asignación de clases a profesores
- Control de acceso por clase
- Passwords hasheados con Werkzeug

#### Interfaz de Usuario
- Diseño responsive con Bootstrap 5 (tema oscuro)
- Iconos Font Awesome 6
- Notificaciones toast en tiempo real
- Estados de carga en botones
- Actualizaciones sin recarga de página (AJAX)
- Recarga automática al validar (para actualizar estadísticas)
- Selector de fecha en dashboard

#### Docker y Despliegue
- Dockerfile optimizado para producción
- Docker Compose con volúmenes persistentes
- Script de inicio automatizado (start.sh)
- Healthcheck automático cada 30 segundos
- Variables de entorno configurables
- Soporte para Dockploy/Coolify/Portainer
- Documentación completa de despliegue

#### Documentación
- README.md principal con guía completa
- DOCKER-QUICKSTART.md para inicio rápido
- DOCKPLOY-DEPLOYMENT.md para Dockploy
- README-DOCKER.md para Docker local
- DEPLOYMENT-CHECKLIST.md con lista de verificación
- CONTRIBUTING.md con guía de contribución
- LICENSE MIT
- .gitignore completo

### 🔧 Cambios Técnicos

#### Base de Datos
- Schema SQLite con 4 tablas: students, classes, teachers, daily_meals
- Índices optimizados para consultas frecuentes
- Foreign keys habilitadas
- WAL mode para mejor concurrencia
- Verificación de integridad al inicio

#### Backend
- Flask 3.0 con Gunicorn en producción
- Consultas SQL optimizadas con CASE para contadores
- Manejo de errores robusto con logging
- Validación de datos en servidor
- API endpoints para operaciones AJAX

#### Frontend
- Templates Jinja2 con herencia
- JavaScript vanilla para interactividad
- Fetch API para llamadas asíncronas
- Estados de UI consistentes
- Manejo de errores en cliente

### 🐛 Corregido

- Porcentaje de validación ahora calcula sobre total importado (no sobre "comen hoy")
- "Comen hoy" solo cuenta confirmados presentes (excluye ausentes)
- Botón "Validar Toda la Clase" funciona incluso si ya hay validaciones
- Exportación con formato idéntico al importado (COM/EXT en mayúsculas)
- Nombre de archivo exportado sin fecha añadida
- Consultas SQL alineadas para evitar conteos duplicados
- Ausentes aparecen correctamente en todas las vistas
- Validación permite re-validar estudiantes

### 🔒 Seguridad

- Contraseñas nunca almacenadas en texto plano
- SESSION_SECRET obligatorio en producción
- Headers de seguridad con ProxyFix
- Validación de entrada en todas las rutas
- Prevención de SQL injection con queries parametrizadas
- CSRF protection habilitado

### 📊 Rendimiento

- Base de datos optimizada con índices
- Consultas SQL eficientes con JOINs
- Cacheo deshabilitado para datos en tiempo real
- Gunicorn con múltiples workers
- Compresión de respuestas HTTP

## [Unreleased]

### Planeado para Futuras Versiones

- Tests unitarios y de integración
- API REST completa con autenticación JWT
- Exportación a PDF de reportes
- Notificaciones por email
- Dashboard con gráficos interactivos (Chart.js)
- Soporte multi-idioma (i18n)
- Modo offline (Progressive Web App)
- Integración con sistemas escolares externos
- Backup automático de base de datos
- Auditoria de cambios (changelog de modificaciones)
- Filtros avanzados en reportes
- Búsqueda de estudiantes
- Estadísticas históricas
- Calendario de comedor
- Gestión de menús

---

## Tipos de Cambios

- **Añadido** - Para funcionalidades nuevas
- **Cambiado** - Para cambios en funcionalidades existentes
- **Obsoleto** - Para funcionalidades que pronto se eliminarán
- **Eliminado** - Para funcionalidades eliminadas
- **Corregido** - Para corrección de bugs
- **Seguridad** - En caso de vulnerabilidades

[1.0.0]: https://github.com/tu-usuario/ComedorEscolar/releases/tag/v1.0.0
