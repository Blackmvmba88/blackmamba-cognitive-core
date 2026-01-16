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
from blackmamba.memory.technical_store import TechnicalMemoryStore
from blackmamba.domains.text_analysis import TextAnalysisDomain
from blackmamba.domains.event_processing import EventProcessingDomain
from blackmamba.domains.electronics_repair import ElectronicsRepairDomain
from blackmamba.core.technical_types import (
    BoardType,
    FaultType,
    RepairActionType,
    OutcomeStatus,
    RepairOutcome,
    RepairAction,
)
from blackmamba.api.models import (
    TextInputRequest,
    EventInputRequest,
    ProcessingResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    StatusResponse,
    TechnicalEventRequest,
    RepairOutcomeRequest,
    SimilarCasesRequest,
    ActionSuccessRateRequest,
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
technical_memory = TechnicalMemoryStore(persist_path="./data/technical_memory.json")
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
engine.register_domain_processor(ElectronicsRepairDomain())


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


# Technical endpoints for iaRealidad integration
@app.post("/technical/event", response_model=ProcessingResponse)
async def process_technical_event(request: TechnicalEventRequest):
    """
    Process technical event from iaRealidad
    
    This endpoint receives structured technical data such as:
    - Measurements (voltage, current, etc.)
    - Symptoms and diagnostics
    - Board events
    
    Args:
        request: Technical event request
        
    Returns:
        Diagnostic response with recommendations
    """
    try:
        # Build event data
        event_data = {
            "event_type": request.event_type,
        }
        
        if request.board_type:
            event_data["board"] = request.board_type
        if request.measurement_type:
            event_data["measurement_type"] = request.measurement_type
        if request.value is not None:
            event_data["value"] = request.value
        if request.expected_value is not None:
            event_data["expected"] = request.expected_value
        if request.unit:
            event_data["unit"] = request.unit
        if request.location:
            event_data["location"] = request.location
        if request.description:
            event_data["description"] = request.description
        if request.severity:
            event_data["severity"] = request.severity
        
        # Create input
        input_data = await input_processor.process_event(
            event_type=request.event_type,
            event_data=event_data,
            metadata=request.metadata
        )
        
        # Process through engine
        response = await engine.process(input_data)
        
        # Store case in technical memory if it's a diagnostic
        if response.content.get("case_id"):
            # The case is already created by ElectronicsRepairDomain
            # We can optionally store it here for tracking
            pass
        
        return ProcessingResponse(
            response_id=response.id,
            input_id=response.input_id,
            content=response.content,
            confidence=response.confidence,
            domain=response.metadata.get("domain"),
            timestamp=response.timestamp,
        )
    except Exception as e:
        logger.error(f"Error processing technical event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/technical/outcome")
async def report_repair_outcome(request: RepairOutcomeRequest):
    """
    Report outcome of a repair action
    
    This endpoint allows iaRealidad to report back the results of repair
    actions, enabling the system to learn from experience.
    
    Args:
        request: Repair outcome request
        
    Returns:
        Confirmation and updated statistics
    """
    try:
        # Parse actions
        actions = []
        for action_data in request.actions_taken:
            action = RepairAction(**action_data)
            actions.append(action)
        
        # Create outcome
        outcome = RepairOutcome(
            case_id=request.case_id,
            actions_taken=actions,
            status=OutcomeStatus(request.status),
            actual_time_minutes=request.actual_time_minutes,
            actual_cost=request.actual_cost,
            notes=request.notes or "",
            success_indicators=request.success_indicators or {}
        )
        
        # Store in technical memory
        outcome_id = await technical_memory.store_outcome(outcome)
        
        # Get updated stats
        stats = await technical_memory.get_technical_stats()
        
        return JSONResponse(content={
            "outcome_id": outcome_id,
            "case_id": request.case_id,
            "status": "recorded",
            "overall_success_rate": stats.get("overall_success_rate", 0.0),
            "total_cases": stats.get("total_cases", 0)
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        logger.error(f"Error reporting outcome: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/technical/similar-cases")
async def find_similar_cases(request: SimilarCasesRequest):
    """
    Find similar past cases
    
    Searches historical data for cases with similar board types and faults.
    Useful for leveraging past experience.
    
    Args:
        request: Similar cases request
        
    Returns:
        List of similar cases with outcomes
    """
    try:
        # Parse board type and faults
        board_type = BoardType(request.board_type)
        faults = [FaultType(f) for f in request.suspected_faults]
        
        # Search for similar cases
        similar = await technical_memory.find_similar_cases(
            board_type=board_type,
            suspected_faults=faults,
            limit=request.limit or 5
        )
        
        return JSONResponse(content={
            "count": len(similar),
            "cases": similar
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        logger.error(f"Error finding similar cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/technical/action-success-rate")
async def get_action_success_rate(request: ActionSuccessRateRequest):
    """
    Get success rate for a repair action
    
    Returns statistics about how successful a particular repair action
    has been in the past, optionally filtered by fault and board type.
    
    Args:
        request: Action success rate request
        
    Returns:
        Success rate statistics
    """
    try:
        action_type = RepairActionType(request.action_type)
        fault_type = FaultType(request.fault_type) if request.fault_type else None
        board_type = BoardType(request.board_type) if request.board_type else None
        
        stats = await technical_memory.get_action_success_rate(
            action_type=action_type,
            fault_type=fault_type,
            board_type=board_type
        )
        
        return JSONResponse(content=stats)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting action success rate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/technical/stats")
async def get_technical_stats():
    """
    Get technical memory statistics
    
    Returns comprehensive statistics about stored cases, outcomes,
    patterns learned, and overall success rates.
    
    Returns:
        Technical statistics
    """
    try:
        stats = await technical_memory.get_technical_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting technical stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/technical/pattern/{fault_type}")
async def get_fault_pattern(fault_type: str):
    """
    Get learned pattern for a fault type
    
    Returns accumulated knowledge about a specific fault type including
    common symptoms, successful actions, and success rates.
    
    Args:
        fault_type: Type of fault
        
    Returns:
        Pattern data
    """
    try:
        fault = FaultType(fault_type)
        pattern = await technical_memory.get_pattern(fault)
        
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        return JSONResponse(content=pattern.model_dump())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid fault type")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pattern: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
