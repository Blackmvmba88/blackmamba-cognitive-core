"""
API models for request/response schemas
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TextInputRequest(BaseModel):
    """Request model for text input"""

    text: str = Field(description="Text content to process")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class AudioInputRequest(BaseModel):
    """Request model for audio input"""

    format: str = Field(default="wav", description="Audio format")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class EventInputRequest(BaseModel):
    """Request model for event input"""

    event_type: str = Field(description="Type of event")
    data: Dict[str, Any] = Field(description="Event data")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class ProcessingResponse(BaseModel):
    """Response model for processed inputs"""

    response_id: str = Field(description="Unique response identifier")
    input_id: str = Field(description="Reference to input")
    content: Dict[str, Any] = Field(description="Response content")
    confidence: float = Field(description="Confidence score")
    domain: Optional[str] = Field(default=None, description="Processing domain")
    timestamp: datetime = Field(description="Response timestamp")


class MemorySearchRequest(BaseModel):
    """Request model for memory search"""

    tags: Optional[List[str]] = Field(default=None, description="Tags to search for")
    type: Optional[str] = Field(default=None, description="Memory type filter")
    content_contains: Optional[str] = Field(default=None, description="Content search term")


class MemorySearchResponse(BaseModel):
    """Response model for memory search"""

    results: List[Dict[str, Any]] = Field(description="Search results")
    count: int = Field(description="Number of results")


class StatusResponse(BaseModel):
    """Response model for system status"""

    status: str = Field(description="System status")
    version: str = Field(description="System version")
    domains: List[str] = Field(description="Available domains")
    memory_enabled: bool = Field(description="Whether memory is enabled")


class TechnicalEventRequest(BaseModel):
    """Request model for technical event from iaRealidad"""

    event_type: str = Field(description="Type of technical event (measurement, diagnosis, symptom)")
    board_type: Optional[str] = Field(default=None, description="Type of board (ESP32, Arduino, etc)")
    measurement_type: Optional[str] = Field(default=None, description="Type of measurement")
    value: Optional[float] = Field(default=None, description="Measured value")
    expected_value: Optional[float] = Field(default=None, description="Expected value")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    location: Optional[str] = Field(default=None, description="Location on board")
    description: Optional[str] = Field(default=None, description="Text description of issue")
    severity: Optional[int] = Field(default=3, ge=1, le=5, description="Severity (1-5)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class RepairOutcomeRequest(BaseModel):
    """Request model for reporting repair outcome"""

    case_id: str = Field(description="ID of diagnostic case")
    status: str = Field(description="Outcome status (success, failure, partial_success)")
    actions_taken: List[Dict[str, Any]] = Field(description="Actions that were taken")
    actual_time_minutes: Optional[int] = Field(default=None, description="Actual time taken")
    actual_cost: Optional[float] = Field(default=None, description="Actual cost")
    notes: Optional[str] = Field(default="", description="Additional notes")
    success_indicators: Optional[Dict[str, Any]] = Field(default=None, description="Success metrics")


class SimilarCasesRequest(BaseModel):
    """Request model for finding similar cases"""

    board_type: str = Field(description="Type of board")
    suspected_faults: List[str] = Field(description="List of suspected faults")
    limit: Optional[int] = Field(default=5, description="Maximum number of results")


class ActionSuccessRateRequest(BaseModel):
    """Request model for action success rate"""

    action_type: str = Field(description="Type of repair action")
    fault_type: Optional[str] = Field(default=None, description="Optional fault type filter")
    board_type: Optional[str] = Field(default=None, description="Optional board type filter")
