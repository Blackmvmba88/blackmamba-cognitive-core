"""Unit tests for input processor"""
import pytest
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.types import InputType


@pytest.mark.asyncio
async def test_process_text(input_processor):
    """Test text input processing"""
    text = "Este es un texto de prueba"
    input_data = await input_processor.process_text(text)
    
    assert input_data.type == InputType.TEXT
    assert input_data.content["text"] == text
    assert input_data.content["length"] == len(text)
    assert input_data.id is not None


@pytest.mark.asyncio
async def test_process_text_with_metadata(input_processor):
    """Test text input processing with metadata"""
    text = "Texto con metadatos"
    metadata = {"source": "test", "priority": "high"}
    
    input_data = await input_processor.process_text(text, metadata=metadata)
    
    assert input_data.metadata == metadata


@pytest.mark.asyncio
async def test_process_audio(input_processor):
    """Test audio input processing"""
    audio_data = b"fake audio data"
    input_data = await input_processor.process_audio(audio_data, format="mp3")
    
    assert input_data.type == InputType.AUDIO
    assert input_data.content["format"] == "mp3"
    assert input_data.content["size_bytes"] == len(audio_data)


@pytest.mark.asyncio
async def test_process_event(input_processor):
    """Test event input processing"""
    event_type = "user_login"
    event_data = {"user_id": "123", "timestamp": "2024-01-01"}
    
    input_data = await input_processor.process_event(event_type, event_data)
    
    assert input_data.type == InputType.EVENT
    assert input_data.content["event_type"] == event_type
    assert input_data.content["data"] == event_data


@pytest.mark.asyncio
async def test_validate_text_input(input_processor):
    """Test text input validation"""
    input_data = await input_processor.process_text("Valid text")
    
    is_valid = await input_processor.validate_input(input_data)
    assert is_valid is True


@pytest.mark.asyncio
async def test_validate_audio_input(input_processor):
    """Test audio input validation"""
    input_data = await input_processor.process_audio(b"audio data")
    
    is_valid = await input_processor.validate_input(input_data)
    assert is_valid is True


@pytest.mark.asyncio
async def test_validate_event_input(input_processor):
    """Test event input validation"""
    input_data = await input_processor.process_event("test_event", {"key": "value"})
    
    is_valid = await input_processor.validate_input(input_data)
    assert is_valid is True
