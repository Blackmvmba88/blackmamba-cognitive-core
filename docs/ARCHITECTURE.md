# Arquitectura del Sistema Cognitivo BlackMamba

## Visión General

BlackMamba Cognitive Core es un sistema cognitivo modular diseñado para procesar entradas diversas (texto, audio, eventos), analizarlas y generar respuestas inteligentes. La arquitectura está basada en dominios, lo que permite una extensibilidad y escalabilidad óptimas.

## Componentes Principales

### 1. Core Engine (`blackmamba/core/`)

El motor cognitivo principal que coordina todo el procesamiento.

#### `CognitiveEngine`
- Orquesta el flujo completo de procesamiento
- Coordina múltiples procesadores de dominio
- Gestiona el contexto de procesamiento
- Integra con el sistema de memoria

#### `InputProcessor`
- Normaliza entradas diversas (texto, audio, eventos)
- Valida entradas antes del procesamiento
- Convierte datos crudos en objetos `Input` estructurados

#### `ResponseGenerator`
- Genera respuestas inteligentes basadas en análisis
- Aplica estrategias de respuesta específicas por dominio
- Calcula puntuaciones de confianza

### 2. Procesadores de Dominio (`blackmamba/domains/`)

Componentes especializados para diferentes tipos de tareas.

#### Interfaz `DomainProcessor`
Todos los procesadores de dominio implementan:
- `can_handle()`: Determina si puede procesar una entrada
- `analyze()`: Analiza la entrada y extrae información
- `synthesize()`: Genera una respuesta basada en el análisis

#### Dominios Implementados

**TextAnalysisDomain**
- Análisis de texto en español
- Métricas: conteo de palabras, complejidad, sentimiento
- Detección de patrones lingüísticos

**EventProcessingDomain**
- Procesamiento de eventos del sistema
- Cálculo de prioridad automático
- Detección de patrones de eventos
- Generación de recomendaciones

### 3. Sistema de Memoria (`blackmamba/memory/`)

Almacenamiento persistente para contexto y aprendizaje.

#### `InMemoryStore`
- Almacenamiento en memoria con persistencia a disco
- Búsqueda por tags y contenido
- Estadísticas de acceso
- Formato JSON para serialización

**Características:**
- Indexación por tags
- Búsqueda de texto completo
- Seguimiento de accesos
- Persistencia automática

### 4. API REST (`blackmamba/api/`)

Interfaz HTTP para interacción con el sistema.

#### Endpoints Principales

```
GET  /               - Estado del sistema
GET  /health         - Health check
POST /process/text   - Procesar texto
POST /process/audio  - Procesar audio
POST /process/event  - Procesar evento
POST /memory/search  - Buscar en memoria
GET  /memory/stats   - Estadísticas de memoria
```

## Flujo de Procesamiento

```
1. Entrada (Input)
   ↓
2. Validación (InputProcessor)
   ↓
3. Selección de Dominio (CognitiveEngine)
   ↓
4. Análisis (DomainProcessor.analyze)
   ↓
5. Almacenamiento en Memoria (MemoryStore)
   ↓
6. Síntesis (DomainProcessor.synthesize)
   ↓
7. Generación de Respuesta (ResponseGenerator)
   ↓
8. Respuesta (Response)
```

## Tipos de Datos Principales

### Input
```python
{
    "id": str,
    "type": "text" | "audio" | "event",
    "content": dict,
    "metadata": dict,
    "timestamp": datetime
}
```

### ProcessingContext
```python
{
    "input_id": str,
    "stage": ProcessingStage,
    "domain": str,
    "memory_refs": [str],
    "analysis_results": dict
}
```

### Response
```python
{
    "id": str,
    "input_id": str,
    "content": dict,
    "confidence": float,
    "metadata": dict,
    "timestamp": datetime
}
```

## Extensibilidad

### Agregar un Nuevo Dominio

1. Crear clase que implemente `DomainProcessor`
2. Implementar métodos requeridos:
   - `domain_name` (property)
   - `can_handle()`
   - `analyze()`
   - `synthesize()`
3. Registrar con `engine.register_domain_processor()`

### Ejemplo:

```python
from blackmamba.core.interfaces import DomainProcessor

class CustomDomain(DomainProcessor):
    @property
    def domain_name(self) -> str:
        return "custom_domain"
    
    async def can_handle(self, input_data, context):
        # Lógica de selección
        return True
    
    async def analyze(self, input_data, context):
        # Lógica de análisis
        return {"analysis": "data"}
    
    async def synthesize(self, input_data, context, analysis):
        # Lógica de síntesis
        return response_object
```

## Configuración

Variables de entorno disponibles:

```bash
COGNITIVE_API_HOST=0.0.0.0
COGNITIVE_API_PORT=8000
COGNITIVE_MEMORY_PATH=./data/memory.json
COGNITIVE_MEMORY_ENABLED=true
COGNITIVE_LOG_LEVEL=INFO
COGNITIVE_MAX_TEXT_LENGTH=10000
```

## Escalabilidad

### Estrategias de Escalado

1. **Horizontal**: Múltiples instancias del API detrás de un load balancer
2. **Vertical**: Procesamiento asíncrono para manejar más carga
3. **Memoria Distribuida**: Usar Redis/Postgres en lugar de InMemoryStore
4. **Procesamiento por Lotes**: Queue system para procesamiento asíncrono

### Consideraciones de Performance

- Procesamiento asíncrono en todos los niveles
- Cache de resultados frecuentes
- Lazy loading de modelos pesados
- Paginación en búsquedas de memoria

## Seguridad

- Validación de entrada con Pydantic
- Límites de tamaño para audio/texto
- Sanitización de contenido
- Rate limiting (a implementar)
- Autenticación/Autorización (a implementar)

## Monitoreo y Observabilidad

- Logging estructurado con niveles
- Métricas de procesamiento
- Estadísticas de memoria
- Health checks para deployments
