"""
Base types and data structures for the cognitive system
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class InputType(str, Enum):
    """Types of input the system can process"""
    TEXT = "text"
    AUDIO = "audio"
    EVENT = "event"


class ProcessingStage(str, Enum):
    """Stages in the processing pipeline"""
    RECEIVED = "received"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class Input(BaseModel):
    """Represents an input to the cognitive system"""
    id: str = Field(description="Unique identifier for this input")
    type: InputType = Field(description="Type of input")
    content: Dict[str, Any] = Field(description="The actual input content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProcessingContext(BaseModel):
    """Context maintained during processing"""
    input_id: str
    stage: ProcessingStage = ProcessingStage.RECEIVED
    domain: Optional[str] = None
    memory_refs: List[str] = Field(default_factory=list)
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Response(BaseModel):
    """Represents a response from the cognitive system"""
    id: str = Field(description="Unique identifier for this response")
    input_id: str = Field(description="Reference to the input that triggered this")
    content: Dict[str, Any] = Field(description="The response content")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MemoryEntry(BaseModel):
    """Represents a memory entry in persistent storage"""
    id: str
    type: str
    content: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    related_inputs: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_count: int = 0
    last_accessed: Optional[datetime] = None
