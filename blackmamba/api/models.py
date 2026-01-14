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
