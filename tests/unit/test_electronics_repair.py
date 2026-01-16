"""
Tests for electronics repair domain
"""

import pytest
from blackmamba.core.types import Input, InputType, ProcessingContext, ProcessingStage
from blackmamba.domains.electronics_repair import ElectronicsRepairDomain
from blackmamba.core.technical_types import (
    BoardType,
    FaultType,
    MeasurementType,
    Measurement,
)


@pytest.fixture
def repair_domain():
    """Fixture for electronics repair domain"""
    return ElectronicsRepairDomain()


@pytest.fixture
def measurement_event():
    """Fixture for measurement event"""
    return Input(
        id="test_measurement_1",
        type=InputType.EVENT,
        content={
            "event_type": "measurement",
            "board": "ESP32",
            "measurement_type": "voltage",
            "value": 3.1,
            "expected": 5.0,
            "unit": "V",
            "location": "VCC"
        }
    )


@pytest.fixture
def text_symptom():
    """Fixture for text symptom"""
    return Input(
        id="test_text_1",
        type=InputType.TEXT,
        content={
            "text": "ESP32 no arranca después de flashear firmware"
        }
    )


@pytest.fixture
def processing_context():
    """Fixture for processing context"""
    return ProcessingContext(
        input_id="test_input_1",
        stage=ProcessingStage.ANALYZING
    )


@pytest.mark.asyncio
async def test_domain_name(repair_domain):
    """Test domain name property"""
    assert repair_domain.domain_name == "electronics_repair"


@pytest.mark.asyncio
async def test_can_handle_measurement_event(repair_domain, measurement_event, processing_context):
    """Test that domain can handle measurement events"""
    can_handle = await repair_domain.can_handle(measurement_event, processing_context)
    assert can_handle is True


@pytest.mark.asyncio
async def test_can_handle_text_symptom(repair_domain, text_symptom, processing_context):
    """Test that domain can handle technical text"""
    can_handle = await repair_domain.can_handle(text_symptom, processing_context)
    assert can_handle is True


@pytest.mark.asyncio
async def test_cannot_handle_non_technical_text(repair_domain, processing_context):
    """Test that domain rejects non-technical text"""
    non_technical = Input(
        id="test_non_tech",
        type=InputType.TEXT,
        content={"text": "Hello, how are you today?"}
    )
    can_handle = await repair_domain.can_handle(non_technical, processing_context)
    assert can_handle is False


@pytest.mark.asyncio
async def test_analyze_measurement_event(repair_domain, measurement_event, processing_context):
    """Test analysis of measurement event"""
    analysis = await repair_domain.analyze(measurement_event, processing_context)
    
    assert "measurements" in analysis
    assert "suspected_faults" in analysis
    assert "confidence" in analysis
    assert "board_type" in analysis
    
    assert analysis["board_type"] == BoardType.ESP32
    assert len(analysis["measurements"]) > 0
    assert analysis["confidence"] > 0


@pytest.mark.asyncio
async def test_analyze_text_symptom(repair_domain, text_symptom, processing_context):
    """Test analysis of text symptom"""
    analysis = await repair_domain.analyze(text_symptom, processing_context)
    
    assert "symptoms" in analysis
    assert "suspected_faults" in analysis
    assert "board_type" in analysis
    
    assert analysis["board_type"] == BoardType.ESP32
    assert len(analysis["symptoms"]) > 0
    # Should detect "no arranca" pattern
    assert any(fault in [FaultType.NO_BOOT, FaultType.CORRUPTED_FIRMWARE] 
               for fault in analysis["suspected_faults"])


@pytest.mark.asyncio
async def test_diagnose_low_voltage(repair_domain, measurement_event, processing_context):
    """Test diagnosis of low voltage condition"""
    analysis = await repair_domain.analyze(measurement_event, processing_context)
    
    # Should detect low voltage issue
    assert FaultType.LOW_VOLTAGE in analysis["suspected_faults"] or \
           FaultType.NO_POWER in analysis["suspected_faults"]
    
    # Should have reasonable confidence
    assert 0.5 <= analysis["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_synthesize_creates_response(repair_domain, measurement_event, processing_context):
    """Test synthesis creates proper response"""
    analysis = await repair_domain.analyze(measurement_event, processing_context)
    response = await repair_domain.synthesize(measurement_event, processing_context, analysis)
    
    assert response.input_id == measurement_event.id
    assert response.confidence > 0
    
    content = response.content
    assert "case_id" in content
    assert "board_type" in content
    assert "diagnosis" in content
    assert "recommendations" in content
    assert "next_steps" in content


@pytest.mark.asyncio
async def test_recommendations_generated(repair_domain, measurement_event, processing_context):
    """Test that recommendations are generated"""
    analysis = await repair_domain.analyze(measurement_event, processing_context)
    response = await repair_domain.synthesize(measurement_event, processing_context, analysis)
    
    recommendations = response.content["recommendations"]
    assert len(recommendations) > 0
    
    # Check recommendation structure
    for rec in recommendations:
        assert "action" in rec
        assert "reason" in rec
        assert "priority" in rec


@pytest.mark.asyncio
async def test_measurement_out_of_range_detection():
    """Test measurement out of range detection"""
    measurement = Measurement(
        type=MeasurementType.VOLTAGE,
        value=3.0,
        unit="V",
        expected_value=5.0,
        expected_unit="V",
        location="VCC"
    )
    
    assert measurement.is_out_of_range() is True


@pytest.mark.asyncio
async def test_measurement_in_range():
    """Test measurement in range"""
    measurement = Measurement(
        type=MeasurementType.VOLTAGE,
        value=5.1,
        unit="V",
        expected_value=5.0,
        expected_unit="V",
        location="VCC"
    )
    
    # Within 10% tolerance
    assert measurement.is_out_of_range() is False


@pytest.mark.asyncio
async def test_board_type_parsing(repair_domain):
    """Test board type parsing from string"""
    assert repair_domain._parse_board_type("ESP32") == BoardType.ESP32
    assert repair_domain._parse_board_type("arduino") == BoardType.ARDUINO
    assert repair_domain._parse_board_type("unknown") == BoardType.UNKNOWN


@pytest.mark.asyncio
async def test_knowledge_base_initialized(repair_domain):
    """Test that knowledge base is initialized"""
    kb = repair_domain._knowledge_base
    
    assert "voltage_patterns" in kb
    assert "symptom_patterns" in kb
    assert "board_specific" in kb
    
    # Check voltage patterns exist
    assert "low_voltage" in kb["voltage_patterns"]
    assert "no_voltage" in kb["voltage_patterns"]
    
    # Check board specific data
    assert BoardType.ESP32 in kb["board_specific"]
