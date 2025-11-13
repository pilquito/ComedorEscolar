# Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Gestión de Comedor Escolar!

## 🚀 Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/ComedorEscolar.git
cd ComedorEscolar
```

### 2. Crear Rama

```bash
git checkout -b feature/mi-nueva-funcionalidad
# o
git checkout -b fix/correcion-bug
```

Convenciones de nombres de ramas:
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bugs
- `docs/` - Documentación
- `refactor/` - Refactorización de código
- `test/` - Añadir o mejorar tests

### 3. Desarrollar

```bash
# Instalar dependencias
pip install -r docker-requirements.txt

# Iniciar aplicación en modo desarrollo
export FLASK_ENV=development
python main.py
```

### 4. Commit

Usa mensajes de commit descriptivos:

```bash
git commit -m "feat: añadir exportación a PDF"
git commit -m "fix: corregir cálculo de porcentaje de validación"
git commit -m "docs: actualizar guía de instalación"
```

Convenciones:
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `style:` - Cambios de formato (sin afectar código)
- `refactor:` - Refactorización de código
- `test:` - Añadir o modificar tests
- `chore:` - Tareas de mantenimiento

### 5. Push y Pull Request

```bash
git push origin feature/mi-nueva-funcionalidad
```

Luego crear Pull Request en GitHub con:
- Título descriptivo
- Descripción de cambios
- Referencias a issues relacionados

## 📋 Checklist de Pull Request

- [ ] El código sigue el estilo del proyecto
- [ ] He probado los cambios localmente
- [ ] He actualizado la documentación si es necesario
- [ ] He añadido tests si es necesario
- [ ] Los tests existentes pasan
- [ ] No hay errores de linting
- [ ] He actualizado CHANGELOG.md

## 🎨 Estilo de Código

### Python
- Seguir PEP 8
- Usar 4 espacios para indentación
- Máximo 100 caracteres por línea
- Docstrings para funciones públicas

```python
def funcion_ejemplo(parametro: str) -> dict:
    """
    Descripción breve de la función.
    
    Args:
        parametro: Descripción del parámetro
        
    Returns:
        Descripción del retorno
    """
    resultado = {"key": "value"}
    return resultado
```

### HTML/Templates
- Usar 2 espacios para indentación
- Atributos en minúsculas
- Comillas dobles para atributos

### CSS
- Usar clases de Bootstrap cuando sea posible
- Nombrar clases en kebab-case
- Agrupar propiedades relacionadas

## 🧪 Tests

```bash
# Ejecutar tests (cuando estén implementados)
pytest tests/

# Coverage
pytest --cov=. tests/
```

## 📝 Documentación

- Actualizar README.md si cambias funcionalidad
- Comentar código complejo
- Mantener documentación sincronizada

## 🐛 Reportar Bugs

Usa GitHub Issues con:
- Descripción clara del bug
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si aplica
- Versión de Python
- Sistema operativo

## 💡 Sugerir Funcionalidades

Usa GitHub Issues con:
- Descripción detallada
- Casos de uso
- Beneficios esperados
- Posibles implementaciones

## ❓ Preguntas

Para preguntas sobre el código:
1. Revisa la documentación
2. Busca en Issues cerrados
3. Abre un nuevo Issue con etiqueta "question"

## 📜 Código de Conducta

- Ser respetuoso y profesional
- Aceptar críticas constructivas
- Enfocarse en lo mejor para el proyecto
- Ayudar a otros contribuidores

## 🎯 Prioridades

Contribuciones especialmente bienvenidas:
- Tests unitarios y de integración
- Documentación y ejemplos
- Corrección de bugs
- Mejoras de rendimiento
- Accesibilidad
- Internacionalización

## 🔍 Revisar Pull Requests

Si quieres ayudar revisando:
- Prueba los cambios localmente
- Verifica que sigan las guías de estilo
- Revisa la lógica del código
- Sugiere mejoras constructivamente

## 📧 Contacto

Para preguntas sobre contribuciones, abre un Issue en GitHub.

---

¡Gracias por contribuir! 🎉
