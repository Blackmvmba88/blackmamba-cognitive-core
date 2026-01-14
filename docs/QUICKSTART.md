# Guía de Inicio Rápido

Esta guía te ayudará a empezar a usar BlackMamba Cognitive Core en menos de 5 minutos.

## 1. Instalación

### Opción A: Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/Blackmvmba88/blackmamba-cognitive-core.git
cd blackmamba-cognitive-core

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .
```

### Opción B: Instalación con Docker

```bash
git clone https://github.com/Blackmvmba88/blackmamba-cognitive-core.git
cd blackmamba-cognitive-core
./scripts/deploy.sh
```

## 2. Primer Ejemplo: Procesamiento de Texto

Crea un archivo `mi_ejemplo.py`:

```python
import asyncio
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.domains.text_analysis import TextAnalysisDomain

async def main():
    # Inicializar
    processor = InputProcessor()
    engine = CognitiveEngine(input_processor=processor)
    engine.register_domain_processor(TextAnalysisDomain())
    
    # Procesar texto
    input_data = await processor.process_text(
        "Hola, este es mi primer texto en BlackMamba!"
    )
    response = await engine.process(input_data)
    
    # Ver resultados
    print(f"Respuesta: {response.content}")
    print(f"Confianza: {response.confidence}")

asyncio.run(main())
```

Ejecutar:
```bash
python mi_ejemplo.py
```

## 3. Usar la API REST

### Iniciar el servidor:

```bash
python scripts/start_server.py
```

El servidor estará disponible en `http://localhost:8000`

### Probar con curl:

```bash
# Procesar texto
curl -X POST http://localhost:8000/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "La IA está cambiando el mundo"}'

# Procesar evento
curl -X POST http://localhost:8000/process/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_action",
    "data": {"action": "click", "button": "submit"}
  }'
```

### Documentación interactiva:

Visita `http://localhost:8000/docs` para ver la documentación Swagger completa.

## 4. Ejemplos Incluidos

El proyecto incluye varios ejemplos funcionales:

```bash
# Procesamiento de texto
python examples/basic_text_processing.py

# Procesamiento de eventos
python examples/event_processing.py

# Cliente API
python examples/api_client.py
```

## 5. Ejecutar Tests

```bash
# Todos los tests
pytest tests/

# Solo tests unitarios
pytest tests/unit/

# Con cobertura
pytest tests/ --cov=blackmamba --cov-report=html
```

## 6. Crear un Dominio Personalizado

```python
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import Input, ProcessingContext, Response

class MiDominio(DomainProcessor):
    @property
    def domain_name(self) -> str:
        return "mi_dominio_custom"
    
    async def can_handle(self, input_data: Input, context: ProcessingContext) -> bool:
        # Tu lógica aquí
        return True
    
    async def analyze(self, input_data: Input, context: ProcessingContext):
        # Tu análisis aquí
        return {"resultado": "mi_análisis"}
    
    async def synthesize(self, input_data: Input, context: ProcessingContext, analysis):
        # Genera respuesta
        from blackmamba.core.response_generator import ResponseGenerator
        gen = ResponseGenerator()
        return await gen.generate(
            input_id=input_data.id,
            context=context,
            synthesis_data={"response_data": analysis},
            confidence=0.9
        )

# Usar tu dominio
engine.register_domain_processor(MiDominio())
```

## 7. Configuración

Crear archivo `.env`:

```bash
COGNITIVE_API_HOST=0.0.0.0
COGNITIVE_API_PORT=8000
COGNITIVE_MEMORY_PATH=./data/memory.json
COGNITIVE_MEMORY_ENABLED=true
COGNITIVE_LOG_LEVEL=INFO
```

## 8. Despliegue en Producción

### Con Docker Compose:

```bash
docker-compose up -d
```

### Verificar estado:

```bash
curl http://localhost:8000/health
```

## Próximos Pasos

- Lee la [Arquitectura](ARCHITECTURE.md) para entender el diseño
- Consulta la [Guía de la API](API_GUIDE.md) para la referencia completa
- Explora los ejemplos en el directorio `examples/`
- Contribuye al proyecto en GitHub

## Soporte

- Issues: https://github.com/Blackmvmba88/blackmamba-cognitive-core/issues
- Documentación: https://github.com/Blackmvmba88/blackmamba-cognitive-core

¡Empieza a construir aplicaciones cognitivas! 🧠✨
