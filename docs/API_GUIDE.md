# Guía de Uso de la API

## Inicio Rápido

### Iniciar el Servidor

```bash
# Opción 1: Usando el script
python scripts/start_server.py

# Opción 2: Directamente
python -m blackmamba.api.app

# Opción 3: Con parámetros personalizados
python scripts/start_server.py --host 0.0.0.0 --port 8080 --reload
```

El servidor estará disponible en `http://localhost:8000`

### Documentación Interactiva

Accede a la documentación Swagger en: `http://localhost:8000/docs`

## Endpoints

### 1. Estado del Sistema

**GET /**

Obtiene el estado actual del sistema.

```bash
curl http://localhost:8000/
```

Respuesta:
```json
{
  "status": "running",
  "version": "0.1.0",
  "domains": ["text_analysis", "event_processing"],
  "memory_enabled": true
}
```

### 2. Health Check

**GET /health**

Verifica que el servicio está funcionando.

```bash
curl http://localhost:8000/health
```

### 3. Procesar Texto

**POST /process/text**

Procesa entrada de texto y genera análisis inteligente.

```bash
curl -X POST http://localhost:8000/process/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "La inteligencia artificial está transformando el mundo",
    "metadata": {
      "source": "user_input",
      "priority": "high"
    }
  }'
```

Respuesta:
```json
{
  "response_id": "uuid-here",
  "input_id": "uuid-here",
  "content": {
    "type": "response",
    "data": {
      "message": "Análisis de texto completado",
      "word_count": 7,
      "complexity": 0.6,
      "insights": ["Este es un texto con contenido sustancial"]
    },
    "summary": "Analizado texto de 7 palabras",
    "domain": "text_analysis"
  },
  "confidence": 0.85,
  "domain": "text_analysis",
  "timestamp": "2024-01-14T10:30:00Z"
}
```

### 4. Procesar Audio

**POST /process/audio**

Procesa archivos de audio.

```bash
curl -X POST http://localhost:8000/process/audio \
  -F "audio_file=@audio.wav" \
  -F "format=wav"
```

### 5. Procesar Evento

**POST /process/event**

Procesa eventos del sistema.

```bash
curl -X POST http://localhost:8000/process/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_login",
    "data": {
      "user_id": "12345",
      "ip_address": "192.168.1.1",
      "timestamp": "2024-01-14T10:30:00Z"
    },
    "metadata": {
      "source": "auth_service"
    }
  }'
```

Respuesta:
```json
{
  "response_id": "uuid-here",
  "input_id": "uuid-here",
  "content": {
    "type": "response",
    "data": {
      "message": "Evento 'user_login' procesado exitosamente",
      "event_type": "user_login",
      "priority": "medium",
      "actions": [],
      "recommendations": []
    },
    "summary": "Evento user_login analizado con prioridad medium"
  },
  "confidence": 0.75,
  "domain": "event_processing",
  "timestamp": "2024-01-14T10:30:01Z"
}
```

### 6. Buscar en Memoria

**POST /memory/search**

Busca entradas en el sistema de memoria.

```bash
curl -X POST http://localhost:8000/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["text", "text_analysis"],
    "content_contains": "inteligencia"
  }'
```

Parámetros de búsqueda:
- `tags`: Lista de tags para filtrar
- `type`: Tipo de entrada
- `content_contains`: Búsqueda de texto en contenido

Respuesta:
```json
{
  "results": [
    {
      "id": "entry-id",
      "type": "memory",
      "content": {...},
      "tags": ["text"],
      "created_at": "2024-01-14T10:30:00Z"
    }
  ],
  "count": 1
}
```

### 7. Estadísticas de Memoria

**GET /memory/stats**

Obtiene estadísticas del sistema de memoria.

```bash
curl http://localhost:8000/memory/stats
```

Respuesta:
```json
{
  "total_entries": 42,
  "total_accesses": 150,
  "tags": ["text", "event", "audio", "text_analysis"]
}
```

## Ejemplos con Python

### Cliente Básico

```python
import httpx
import asyncio

async def process_text(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/process/text",
            json={"text": text}
        )
        return response.json()

# Uso
result = asyncio.run(process_text("Hola mundo"))
print(result)
```

### Procesamiento por Lotes

```python
import httpx
import asyncio

async def process_batch(texts: list):
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                "http://localhost:8000/process/text",
                json={"text": text}
            )
            for text in texts
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

texts = ["Texto 1", "Texto 2", "Texto 3"]
results = asyncio.run(process_batch(texts))
```

### Monitoreo de Eventos

```python
import httpx
import asyncio
from datetime import datetime

async def send_event(event_type: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/process/event",
            json={
                "event_type": event_type,
                "data": data
            }
        )
        return response.json()

# Uso
event_data = {
    "action": "page_view",
    "page": "/home",
    "user_id": "user123"
}
result = asyncio.run(send_event("user_activity", event_data))
```

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `422 Unprocessable Entity`: Error de validación en la entrada
- `500 Internal Server Error`: Error en el procesamiento
- `503 Service Unavailable`: Servicio no disponible (ej. memoria deshabilitada)

## Límites y Consideraciones

- Texto máximo: 10,000 caracteres (configurable)
- Tamaño máximo de audio: 10 MB (configurable)
- Timeout de request: 30 segundos
- Rate limiting: No implementado (considerar para producción)

## Autenticación

Actualmente el API no requiere autenticación. Para producción, se recomienda implementar:
- API Keys
- OAuth2
- JWT tokens

## Mejores Prácticas

1. **Siempre incluir metadata útil**: Ayuda con el análisis contextual
2. **Usar búsqueda de memoria**: Aprovecha el contexto histórico
3. **Monitorear confianza**: Respuestas con confianza < 0.5 pueden necesitar revisión
4. **Manejar errores apropiadamente**: Implementar retry logic para errores transitorios
5. **Usar procesamiento asíncrono**: Para mejor performance con múltiples requests
