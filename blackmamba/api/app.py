"""
FastAPI application for the cognitive system
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from blackmamba import __version__
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.response_generator import ResponseGenerator
from blackmamba.memory.store import InMemoryStore
from blackmamba.domains.text_analysis import TextAnalysisDomain
from blackmamba.domains.event_processing import EventProcessingDomain
from blackmamba.api.models import (
    TextInputRequest,
    EventInputRequest,
    ProcessingResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    StatusResponse,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BlackMamba Cognitive Core API",
    description="Motor cognitivo modular para construir aplicaciones interactivas basadas en IA",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize cognitive engine
memory_store = InMemoryStore(persist_path="./data/memory.json")
input_processor = InputProcessor()
response_generator = ResponseGenerator()
engine = CognitiveEngine(
    input_processor=input_processor,
    response_generator=response_generator,
    memory_store=memory_store,
)

# Register domain processors
engine.register_domain_processor(TextAnalysisDomain())
engine.register_domain_processor(EventProcessingDomain())


@app.get("/", response_model=StatusResponse)
async def root():
    """Get system status"""
    return StatusResponse(
        status="running",
        version=__version__,
        domains=[p.domain_name for p in engine.domain_processors],
        memory_enabled=engine.memory_store is not None,
    )


@app.post("/process/text", response_model=ProcessingResponse)
async def process_text(request: TextInputRequest):
    """
    Process text input

    Args:
        request: Text input request

    Returns:
        Processing response
    """
    try:
        # Create input
        input_data = await input_processor.process_text(
            text=request.text, metadata=request.metadata
        )

        # Process through engine
        response = await engine.process(input_data)

        return ProcessingResponse(
            response_id=response.id,
            input_id=response.input_id,
            content=response.content,
            confidence=response.confidence,
            domain=response.metadata.get("domain"),
            timestamp=response.timestamp,
        )
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/audio", response_model=ProcessingResponse)
async def process_audio(audio_file: UploadFile = File(...), format: Optional[str] = "wav"):
    """
    Process audio input

    Args:
        audio_file: Audio file upload
        format: Audio format

    Returns:
        Processing response
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()

        # Create input
        input_data = await input_processor.process_audio(
            audio_data=audio_data, format=format, metadata={"filename": audio_file.filename}
        )

        # Process through engine
        response = await engine.process(input_data)

        return ProcessingResponse(
            response_id=response.id,
            input_id=response.input_id,
            content=response.content,
            confidence=response.confidence,
            domain=response.metadata.get("domain"),
            timestamp=response.timestamp,
        )
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/event", response_model=ProcessingResponse)
async def process_event(request: EventInputRequest):
    """
    Process event input

    Args:
        request: Event input request

    Returns:
        Processing response
    """
    try:
        # Create input
        input_data = await input_processor.process_event(
            event_type=request.event_type, event_data=request.data, metadata=request.metadata
        )

        # Process through engine
        response = await engine.process(input_data)

        return ProcessingResponse(
            response_id=response.id,
            input_id=response.input_id,
            content=response.content,
            confidence=response.confidence,
            domain=response.metadata.get("domain"),
            timestamp=response.timestamp,
        )
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/search", response_model=MemorySearchResponse)
async def search_memory(request: MemorySearchRequest):
    """
    Search memory store

    Args:
        request: Memory search request

    Returns:
        Search results
    """
    try:
        if not engine.memory_store:
            raise HTTPException(status_code=503, detail="Memory store not available")

        query = {}
        if request.tags:
            query["tags"] = request.tags
        if request.type:
            query["type"] = request.type
        if request.content_contains:
            query["content_contains"] = request.content_contains

        results = await engine.memory_store.search(query)

        return MemorySearchResponse(results=results, count=len(results))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/stats")
async def get_memory_stats():
    """Get memory statistics"""
    try:
        if not engine.memory_store:
            raise HTTPException(status_code=503, detail="Memory store not available")

        stats = await engine.memory_store.get_stats()
        return JSONResponse(content=stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": __version__}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
