"""
Technical types for electronics repair domain

This module defines the ontology for electronics repair:
- Boards and components
- Measurements and symptoms
- Diagnostic cases
- Repair actions and outcomes
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class BoardType(str, Enum):
    """Types of electronic boards"""
    ESP32 = "ESP32"
    ESP8266 = "ESP8266"
    ARDUINO = "Arduino"
    RASPBERRY_PI = "Raspberry Pi"
    STM32 = "STM32"
    CUSTOM = "Custom"
    UNKNOWN = "Unknown"


class ComponentType(str, Enum):
    """Types of electronic components"""
    VOLTAGE_REGULATOR = "voltage_regulator"
    MICROCONTROLLER = "microcontroller"
    SENSOR = "sensor"
    CAPACITOR = "capacitor"
    RESISTOR = "resistor"
    LED = "led"
    TRANSISTOR = "transistor"
    CRYSTAL = "crystal"
    CONNECTOR = "connector"
    OTHER = "other"


class MeasurementType(str, Enum):
    """Types of measurements"""
    VOLTAGE = "voltage"
    CURRENT = "current"
    RESISTANCE = "resistance"
    FREQUENCY = "frequency"
    TEMPERATURE = "temperature"
    SIGNAL = "signal"


class FaultType(str, Enum):
    """Common fault types"""
    NO_POWER = "no_power"
    LOW_VOLTAGE = "low_voltage"
    HIGH_VOLTAGE = "high_voltage"
    NO_BOOT = "no_boot"
    NO_COMMUNICATION = "no_communication"
    OVERHEATING = "overheating"
    SHORT_CIRCUIT = "short_circuit"
    OPEN_CIRCUIT = "open_circuit"
    INTERMITTENT = "intermittent"
    CORRUPTED_FIRMWARE = "corrupted_firmware"
    SENSOR_FAILURE = "sensor_failure"
    UNKNOWN = "unknown"


class RepairActionType(str, Enum):
    """Types of repair actions"""
    REPLACE_COMPONENT = "replace_component"
    REFLASH_FIRMWARE = "reflash_firmware"
    CHECK_CONNECTION = "check_connection"
    CLEAN_CONTACTS = "clean_contacts"
    RESOLDER = "resolder"
    ADJUST_VOLTAGE = "adjust_voltage"
    RESET_DEVICE = "reset_device"
    UPDATE_SOFTWARE = "update_software"
    REPLACE_POWER_SUPPLY = "replace_power_supply"


class OutcomeStatus(str, Enum):
    """Status of repair outcome"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class Measurement(BaseModel):
    """Represents a technical measurement"""
    type: MeasurementType
    value: float
    unit: str
    expected_value: Optional[float] = None
    expected_unit: Optional[str] = None
    location: str  # Where on the board
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_out_of_range(self) -> bool:
        """Check if measurement is out of expected range"""
        if self.expected_value is None:
            return False
        # Simple tolerance check (±10%)
        tolerance = 0.1
        lower_bound = self.expected_value * (1 - tolerance)
        upper_bound = self.expected_value * (1 + tolerance)
        return not (lower_bound <= self.value <= upper_bound)


class Symptom(BaseModel):
    """Represents a symptom or issue description"""
    description: str
    severity: int = Field(ge=1, le=5, default=3)  # 1=minor, 5=critical
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = Field(default_factory=dict)


class DiagnosticCase(BaseModel):
    """Represents a complete diagnostic case"""
    id: str
    board_type: BoardType
    symptoms: List[Symptom] = Field(default_factory=list)
    measurements: List[Measurement] = Field(default_factory=list)
    suspected_faults: List[FaultType] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RepairAction(BaseModel):
    """Represents a repair action taken"""
    action_type: RepairActionType
    description: str
    target_component: Optional[ComponentType] = None
    target_location: Optional[str] = None
    estimated_time_minutes: Optional[int] = None
    estimated_cost: Optional[float] = None
    performed_at: Optional[datetime] = None


class RepairOutcome(BaseModel):
    """Represents the outcome of a repair"""
    case_id: str
    actions_taken: List[RepairAction]
    status: OutcomeStatus
    actual_time_minutes: Optional[int] = None
    actual_cost: Optional[float] = None
    notes: str = ""
    success_indicators: Dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TechnicalPattern(BaseModel):
    """Represents a learned pattern from past cases"""
    pattern_id: str
    fault_type: FaultType
    common_symptoms: List[str]
    common_measurements: Dict[str, Any]
    recommended_actions: List[RepairActionType]
    success_rate: float = Field(ge=0.0, le=1.0)
    sample_size: int = 0
    board_types: List[BoardType] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
