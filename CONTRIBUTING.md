# Contribuir a BlackMamba Cognitive Core

¡Gracias por tu interés en contribuir! Este documento proporciona pautas para contribuir al proyecto.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor:

1. Verifica que no exista un issue similar
2. Abre un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Versión de Python y dependencias
   - Logs o screenshots si aplican

### Sugerir Mejoras

Para sugerir nuevas características:

1. Abre un issue describiendo:
   - El problema que resuelve
   - Cómo lo implementarías
   - Ejemplos de uso

### Pull Requests

1. **Fork el repositorio**

2. **Crea una rama**
   ```bash
   git checkout -b feature/mi-nueva-caracteristica
   ```

3. **Haz tus cambios**
   - Sigue el estilo de código existente
   - Agrega tests para tu código
   - Actualiza la documentación si es necesario

4. **Ejecuta los tests**
   ```bash
   pytest tests/
   ```

5. **Commit tus cambios**
   ```bash
   git commit -m "feat: descripción clara del cambio"
   ```
   
   Usa prefijos como:
   - `feat:` para nuevas características
   - `fix:` para correcciones
   - `docs:` para documentación
   - `test:` para tests
   - `refactor:` para refactorización

6. **Push y crea el PR**
   ```bash
   git push origin feature/mi-nueva-caracteristica
   ```

## Estándares de Código

### Estilo Python

- Sigue PEP 8
- Usa type hints cuando sea posible
- Máximo 100 caracteres por línea
- Usa docstrings para funciones públicas

Ejemplo:
```python
from typing import Dict, Any

async def process_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input data and return results.
    
    Args:
        input_data: Dictionary containing input information
        
    Returns:
        Dictionary with processed results
    """
    # Implementation
    return {}
```

### Tests

- Escribe tests para todo código nuevo
- Usa pytest y pytest-asyncio
- Nombra tests descriptivamente: `test_<funcionalidad>_<escenario>`
- Organiza en tests unitarios e integración

Ejemplo:
```python
@pytest.mark.asyncio
async def test_process_text_returns_valid_response():
    """Test that text processing returns a valid response"""
    processor = InputProcessor()
    input_data = await processor.process_text("test text")
    assert input_data.type == InputType.TEXT
```

### Documentación

- Actualiza el README si cambias funcionalidad pública
- Agrega docstrings a clases y funciones
- Incluye ejemplos de uso cuando sea útil
- Documenta parámetros de configuración

## Estructura del Proyecto

```
blackmamba/
├── core/              # Motor cognitivo principal
│   ├── engine.py      # Orquestador
│   ├── interfaces.py  # Interfaces base
│   └── types.py       # Tipos de datos
├── domains/           # Procesadores por dominio
├── memory/            # Sistema de memoria
├── api/               # API REST
└── utils/             # Utilidades

tests/
├── unit/              # Tests unitarios
└── integration/       # Tests de integración

examples/              # Ejemplos funcionales
docs/                  # Documentación
scripts/               # Scripts de utilidad
```

## Agregar un Nuevo Dominio

1. Crea archivo en `blackmamba/domains/mi_dominio.py`

2. Implementa la interfaz `DomainProcessor`:
```python
from blackmamba.core.interfaces import DomainProcessor

class MiDominio(DomainProcessor):
    @property
    def domain_name(self) -> str:
        return "mi_dominio"
    
    async def can_handle(self, input_data, context):
        # Lógica de selección
        pass
    
    async def analyze(self, input_data, context):
        # Lógica de análisis
        pass
    
    async def synthesize(self, input_data, context, analysis):
        # Lógica de síntesis
        pass
```

3. Agrega tests en `tests/unit/test_mi_dominio.py`

4. Documenta en `docs/DOMAINS.md`

5. Agrega ejemplo en `examples/`

## Convenciones de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>[scope opcional]: <descripción>

[cuerpo opcional]

[footer opcional]
```

Tipos:
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato (sin cambio de código)
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Tareas de mantenimiento

Ejemplos:
```
feat(domains): add sentiment analysis domain
fix(memory): resolve JSON serialization issue
docs(api): update endpoint documentation
test(core): add tests for input validation
```

## Proceso de Revisión

1. Tu PR será revisado por mantenedores
2. Puede haber comentarios y solicitudes de cambios
3. Una vez aprobado, será merged
4. Los cambios aparecerán en la próxima release

## Código de Conducta

- Sé respetuoso y profesional
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Ayuda a otros contribuidores

## Preguntas

Si tienes preguntas:
- Abre un issue con la etiqueta `question`
- Revisa la documentación existente
- Consulta ejemplos en `examples/`

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la licencia MIT del proyecto.

---

¡Gracias por contribuir a BlackMamba Cognitive Core! 🎉
