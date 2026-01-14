# BlackMamba Cognitive Core

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Motor cognitivo modular para construir aplicaciones interactivas basadas en IA: coordinación, memoria, análisis y síntesis creativa. Arquitectura limpia, escalable y orientada a dominios.

## 🚀 Características

- **Procesamiento Multi-Modal**: Maneja texto, audio y eventos
- **Arquitectura por Dominios**: Procesadores especializados extensibles
- **Memoria Persistente**: Almacenamiento con búsqueda y análisis contextual
- **API REST**: Interfaz completa con FastAPI y documentación interactiva
- **Testing Completo**: Suite de pruebas unitarias e integración
- **Despliegue Simple**: Scripts automatizados y configuración Docker
- **Totalmente Asíncrono**: Alto rendimiento con asyncio
- **Extensible**: Fácil de agregar nuevos dominios y capacidades

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Docker (opcional, para despliegue containerizado)

## 🔧 Instalación

### Instalación Básica

```bash
# Clonar el repositorio
git clone https://github.com/Blackmvmba88/blackmamba-cognitive-core.git
cd blackmamba-cognitive-core

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### Instalación con Docker

```bash
# Construir y desplegar
./scripts/deploy.sh

# O manualmente
docker build -t blackmamba-cognitive-core .
docker-compose up -d
```

## 🎯 Inicio Rápido

### Iniciar el Servidor API

```bash
# Opción 1: Script de inicio
python scripts/start_server.py

# Opción 2: Directamente
python -m blackmamba.api.app

# Opción 3: Con auto-reload para desarrollo
python scripts/start_server.py --reload
```

El servidor estará disponible en `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### Ejemplo Básico con Python

```python
import asyncio
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.domains.text_analysis import TextAnalysisDomain

async def main():
    # Inicializar componentes
    processor = InputProcessor()
    engine = CognitiveEngine(input_processor=processor)
    
    # Registrar dominio
    engine.register_domain_processor(TextAnalysisDomain())
    
    # Procesar texto
    input_data = await processor.process_text(
        "La inteligencia artificial está transformando el mundo"
    )
    response = await engine.process(input_data)
    
    print(f"Respuesta: {response.content}")
    print(f"Confianza: {response.confidence}")

asyncio.run(main())
```

### Ejemplo con la API REST

```bash
# Procesar texto
curl -X POST http://localhost:8000/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, mundo cognitivo!"}'

# Procesar evento
curl -X POST http://localhost:8000/process/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_login",
    "data": {"user_id": "123"}
  }'

# Buscar en memoria
curl -X POST http://localhost:8000/memory/search \
  -H "Content-Type: application/json" \
  -d '{"tags": ["text"]}'
```

## 📚 Documentación

- [Arquitectura del Sistema](docs/ARCHITECTURE.md) - Diseño y componentes
- [Guía de la API](docs/API_GUIDE.md) - Referencia completa de endpoints

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
./scripts/run_tests.sh

# Ejecutar pruebas específicas
pytest tests/unit/
pytest tests/integration/

# Con cobertura
pytest --cov=blackmamba --cov-report=html
```

## 🎨 Ejemplos

El directorio `examples/` contiene ejemplos funcionales:

```bash
# Procesamiento de texto
python examples/basic_text_processing.py

# Procesamiento de eventos
python examples/event_processing.py

# Cliente API
python examples/api_client.py
```

## 🏗️ Arquitectura

```
blackmamba/
├── core/              # Motor cognitivo principal
│   ├── engine.py      # Orquestador principal
│   ├── input_processor.py
│   ├── response_generator.py
│   ├── interfaces.py  # Interfaces base
│   └── types.py       # Tipos de datos
├── domains/           # Procesadores por dominio
│   ├── text_analysis.py
│   └── event_processing.py
├── memory/            # Sistema de memoria
│   └── store.py
├── api/               # API REST
│   ├── app.py
│   └── models.py
└── utils/             # Utilidades
    ├── config.py
    └── logging.py
```

## 🔌 Extensibilidad

### Crear un Nuevo Dominio

```python
from blackmamba.core.interfaces import DomainProcessor

class MiDominio(DomainProcessor):
    @property
    def domain_name(self) -> str:
        return "mi_dominio"
    
    async def can_handle(self, input_data, context):
        # Determinar si este dominio maneja la entrada
        return True
    
    async def analyze(self, input_data, context):
        # Analizar entrada
        return {"resultado": "análisis"}
    
    async def synthesize(self, input_data, context, analysis):
        # Generar respuesta
        return response_object

# Registrar
engine.register_domain_processor(MiDominio())
```

## ⚙️ Configuración

Variables de entorno disponibles:

```bash
COGNITIVE_API_HOST=0.0.0.0          # Host del servidor
COGNITIVE_API_PORT=8000             # Puerto del servidor
COGNITIVE_MEMORY_PATH=./data/memory.json  # Ruta de persistencia
COGNITIVE_MEMORY_ENABLED=true      # Habilitar memoria
COGNITIVE_LOG_LEVEL=INFO           # Nivel de logging
COGNITIVE_MAX_TEXT_LENGTH=10000    # Límite de texto
```

## 🐳 Despliegue con Docker

```bash
# Construcción
docker build -t blackmamba-cognitive-core .

# Ejecución
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  blackmamba-cognitive-core

# Con Docker Compose
docker-compose up -d
```

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

**BlackMamba**
- GitHub: [@Blackmvmba88](https://github.com/Blackmvmba88)

## 🙏 Agradecimientos

- FastAPI por el excelente framework web
- Pydantic por la validación de datos
- La comunidad Python por las herramientas increíbles

## 📞 Soporte

Para preguntas, problemas o sugerencias:
- Abrir un [Issue](https://github.com/Blackmvmba88/blackmamba-cognitive-core/issues)
- Consultar la [documentación](docs/)

---

**BlackMamba Cognitive Core** - Construyendo el futuro de las aplicaciones cognitivas 🧠✨
