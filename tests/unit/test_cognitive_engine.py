"""Unit tests for cognitive engine"""
import pytest
from blackmamba.core.types import InputType


@pytest.mark.asyncio
async def test_engine_process_text(cognitive_engine, input_processor):
    """Test processing text through the engine"""
    input_data = await input_processor.process_text("Este es un texto de prueba")
    
    response = await cognitive_engine.process(input_data)
    
    assert response.input_id == input_data.id
    assert response.confidence > 0
    assert response.content is not None


@pytest.mark.asyncio
async def test_engine_process_event(cognitive_engine, input_processor):
    """Test processing events through the engine"""
    input_data = await input_processor.process_event(
        "user_action",
        {"action": "click", "target": "button"}
    )
    
    response = await cognitive_engine.process(input_data)
    
    assert response.input_id == input_data.id
    assert response.confidence > 0


@pytest.mark.asyncio
async def test_engine_with_memory(cognitive_engine, input_processor):
    """Test that engine stores in memory"""
    input_data = await input_processor.process_text("Texto para memoria")
    
    response = await cognitive_engine.process(input_data)
    
    # Check memory was used
    assert len(response.metadata.get("memory_refs", [])) > 0


@pytest.mark.asyncio
async def test_engine_domain_selection(cognitive_engine, input_processor):
    """Test that appropriate domain is selected"""
    # Text input should select text domain
    text_input = await input_processor.process_text("Texto")
    text_response = await cognitive_engine.process(text_input)
    assert text_response.metadata.get("domain") == "text_analysis"
    
    # Event input should select event domain
    event_input = await input_processor.process_event("test", {})
    event_response = await cognitive_engine.process(event_input)
    assert event_response.metadata.get("domain") == "event_processing"


@pytest.mark.asyncio
async def test_engine_invalid_input(cognitive_engine):
    """Test engine handling of invalid input"""
    from blackmamba.core.types import Input
    
    # Create invalid input
    invalid_input = Input(
        id="test",
        type=InputType.TEXT,
        content={}  # Missing required 'text' field
    )
    
    with pytest.raises(ValueError):
        await cognitive_engine.process(invalid_input)


@pytest.mark.asyncio
async def test_get_memory_context(cognitive_engine, input_processor):
    """Test retrieving memory context"""
    # Process some inputs to populate memory
    await cognitive_engine.process(
        await input_processor.process_text("Primer texto")
    )
    await cognitive_engine.process(
        await input_processor.process_text("Segundo texto")
    )
    
    # Get memory context
    context = await cognitive_engine.get_memory_context(["text"])
    
    assert len(context) > 0
