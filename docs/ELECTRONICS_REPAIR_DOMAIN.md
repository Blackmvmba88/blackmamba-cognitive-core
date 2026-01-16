# Electronics Repair Domain - Integration Guide

## Overview

The **Electronics Repair Domain** extends BlackMamba Cognitive Core with specialized capabilities for diagnosing and repairing electronic boards. It's designed to integrate seamlessly with **iaRealidad** (the sensor/robotics system) to create an operational AI that can:

- **Sense**: Receive measurements and observations from hardware
- **Diagnose**: Analyze symptoms and measurements to identify faults
- **Recommend**: Suggest repair actions based on knowledge and experience
- **Remember**: Store cases and outcomes for continuous learning
- **Improve**: Update patterns and success rates based on feedback

## Architecture

```
iaRealidad → (technical events) → CognitiveCore → (diagnosis + recommendations) → iaRealidad
                                        ↓
                                  Technical Memory
                                  (cases, patterns, outcomes)
```

## Technical Ontology

### Board Types
- ESP32
- ESP8266
- Arduino
- Raspberry Pi
- STM32
- Custom/Unknown

### Fault Types
- `no_power`: Device has no power
- `low_voltage`: Voltage below expected
- `high_voltage`: Voltage above expected
- `no_boot`: Device doesn't boot
- `no_communication`: No I2C/UART/SPI communication
- `overheating`: Device overheating
- `short_circuit`: Electrical short detected
- `open_circuit`: Electrical open detected
- `intermittent`: Intermittent failures
- `corrupted_firmware`: Firmware issues
- `sensor_failure`: Sensor not working

### Measurement Types
- `voltage`: Voltage measurements (V)
- `current`: Current measurements (A)
- `resistance`: Resistance measurements (Ω)
- `frequency`: Frequency measurements (Hz)
- `temperature`: Temperature measurements (°C)
- `signal`: Digital signal analysis

### Repair Actions
- `replace_component`: Replace a faulty component
- `reflash_firmware`: Reflash device firmware
- `check_connection`: Verify connections
- `clean_contacts`: Clean electrical contacts
- `resolder`: Resolder joints
- `adjust_voltage`: Adjust voltage levels
- `reset_device`: Reset the device
- `update_software`: Update software
- `replace_power_supply`: Replace power supply

## API Endpoints

### 1. Process Technical Event

**Endpoint**: `POST /technical/event`

**Purpose**: Send measurements, symptoms, or technical events for diagnosis

**Request Body**:
```json
{
  "event_type": "measurement",
  "board_type": "ESP32",
  "measurement_type": "voltage",
  "value": 3.1,
  "expected_value": 5.0,
  "unit": "V",
  "location": "VCC",
  "description": "Low voltage on VCC pin",
  "severity": 4,
  "metadata": {
    "source": "multimeter",
    "operator": "technician_1"
  }
}
```

**Response**:
```json
{
  "response_id": "resp_123",
  "input_id": "input_456",
  "content": {
    "case_id": "case_789",
    "board_type": "ESP32",
    "diagnosis": {
      "suspected_faults": ["low_voltage", "no_power"],
      "confidence": 0.7,
      "measurements_summary": [
        {
          "type": "voltage",
          "value": 3.1,
          "unit": "V",
          "location": "VCC",
          "expected": 5.0,
          "out_of_range": true
        }
      ]
    },
    "recommendations": [
      {
        "action": "check_connection",
        "reason": "Common fix for low_voltage",
        "priority": "medium"
      },
      {
        "action": "replace_power_supply",
        "reason": "Common fix for low_voltage",
        "priority": "medium"
      }
    ],
    "next_steps": [
      "Verify all measurements are accurate",
      "Start with: check connection",
      "Review ESP32 specific documentation",
      "Document outcome for learning"
    ]
  },
  "confidence": 0.7,
  "domain": "electronics_repair",
  "timestamp": "2026-01-16T08:30:00Z"
}
```

### 2. Report Repair Outcome

**Endpoint**: `POST /technical/outcome`

**Purpose**: Report the result of repair actions for learning

**Request Body**:
```json
{
  "case_id": "case_789",
  "status": "success",
  "actions_taken": [
    {
      "action_type": "check_connection",
      "description": "Checked VCC connection",
      "target_location": "VCC",
      "estimated_time_minutes": 5
    },
    {
      "action_type": "resolder",
      "description": "Resoldered VCC pin",
      "target_location": "VCC",
      "estimated_time_minutes": 10
    }
  ],
  "actual_time_minutes": 15,
  "actual_cost": 5.0,
  "notes": "Cold solder joint on VCC was the issue",
  "success_indicators": {
    "voltage_restored": true,
    "device_boots": true
  }
}
```

**Response**:
```json
{
  "outcome_id": "outcome_123",
  "case_id": "case_789",
  "status": "recorded",
  "overall_success_rate": 0.85,
  "total_cases": 42
}
```

### 3. Find Similar Cases

**Endpoint**: `POST /technical/similar-cases`

**Purpose**: Find past cases with similar symptoms for guidance

**Request Body**:
```json
{
  "board_type": "ESP32",
  "suspected_faults": ["low_voltage", "no_power"],
  "limit": 5
}
```

**Response**:
```json
{
  "count": 3,
  "cases": [
    {
      "case": {
        "id": "case_456",
        "board_type": "ESP32",
        "suspected_faults": ["low_voltage"]
      },
      "outcome": {
        "status": "success",
        "actions_taken": [...]
      },
      "similarity_score": 0.85
    }
  ]
}
```

### 4. Get Action Success Rate

**Endpoint**: `POST /technical/action-success-rate`

**Purpose**: Query success rate for specific repair actions

**Request Body**:
```json
{
  "action_type": "resolder",
  "fault_type": "low_voltage",
  "board_type": "ESP32"
}
```

**Response**:
```json
{
  "action_type": "resolder",
  "total_cases": 15,
  "successful_cases": 12,
  "success_rate": 0.8,
  "filters": {
    "fault_type": "low_voltage",
    "board_type": "ESP32"
  }
}
```

### 5. Get Technical Statistics

**Endpoint**: `GET /technical/stats`

**Purpose**: Get comprehensive statistics about the technical memory

**Response**:
```json
{
  "total_entries": 156,
  "total_accesses": 423,
  "total_cases": 42,
  "total_outcomes": 38,
  "overall_success_rate": 0.85,
  "fault_distribution": {
    "low_voltage": 15,
    "no_boot": 12,
    "no_communication": 8
  },
  "board_distribution": {
    "ESP32": 25,
    "Arduino": 10,
    "ESP8266": 7
  },
  "patterns_learned": 8
}
```

### 6. Get Fault Pattern

**Endpoint**: `GET /technical/pattern/{fault_type}`

**Purpose**: Get learned patterns for a specific fault type

**Example**: `GET /technical/pattern/low_voltage`

**Response**:
```json
{
  "pattern_id": "pattern_low_voltage",
  "fault_type": "low_voltage",
  "common_symptoms": [
    "no boot",
    "intermittent operation"
  ],
  "common_measurements": {},
  "recommended_actions": [
    "check_connection",
    "resolder",
    "replace_power_supply"
  ],
  "success_rate": 0.82,
  "sample_size": 15,
  "board_types": ["ESP32", "Arduino"],
  "last_updated": "2026-01-16T08:30:00Z"
}
```

## Integration Examples

### Example 1: Simple Measurement Event

```python
import requests

# Send measurement from iaRealidad
response = requests.post("http://localhost:8000/technical/event", json={
    "event_type": "measurement",
    "board_type": "ESP32",
    "measurement_type": "voltage",
    "value": 2.8,
    "expected_value": 3.3,
    "unit": "V",
    "location": "3V3"
})

diagnosis = response.json()
print(f"Case ID: {diagnosis['content']['case_id']}")
print(f"Confidence: {diagnosis['confidence']}")
print(f"Suspected faults: {diagnosis['content']['diagnosis']['suspected_faults']}")
print(f"Recommendations: {diagnosis['content']['recommendations']}")
```

### Example 2: Text Symptom Description

```python
# Send text description
response = requests.post("http://localhost:8000/technical/event", json={
    "event_type": "symptom",
    "board_type": "ESP32",
    "description": "ESP32 no arranca después de flashear firmware",
    "severity": 4
})

diagnosis = response.json()
```

### Example 3: Complete Repair Workflow

```python
# 1. Send diagnostic event
event_response = requests.post("http://localhost:8000/technical/event", json={
    "event_type": "measurement",
    "board_type": "ESP32",
    "value": 3.1,
    "expected_value": 5.0,
    "unit": "V",
    "location": "VCC"
})

case_id = event_response.json()["content"]["case_id"]
recommendations = event_response.json()["content"]["recommendations"]

# 2. Perform repair actions based on recommendations
# ... (technician or robot performs actions) ...

# 3. Report outcome
outcome_response = requests.post("http://localhost:8000/technical/outcome", json={
    "case_id": case_id,
    "status": "success",
    "actions_taken": [
        {
            "action_type": "check_connection",
            "description": "Checked and fixed VCC connection"
        }
    ],
    "actual_time_minutes": 10,
    "notes": "Loose connection was the issue"
})

print(f"New success rate: {outcome_response.json()['overall_success_rate']}")
```

### Example 4: Query Similar Cases Before Repair

```python
# Before attempting repair, check similar cases
similar_response = requests.post("http://localhost:8000/technical/similar-cases", json={
    "board_type": "ESP32",
    "suspected_faults": ["low_voltage"],
    "limit": 5
})

similar_cases = similar_response.json()["cases"]
for case in similar_cases:
    print(f"Similar case (score: {case['similarity_score']})")
    if case["outcome"]:
        print(f"  Outcome: {case['outcome']['status']}")
        print(f"  Actions: {[a['action_type'] for a in case['outcome']['actions_taken']]}")
```

## Data Flow

### Diagnostic Flow
```
1. iaRealidad detects issue (measurement, observation)
2. Sends event to /technical/event
3. ElectronicsRepairDomain analyzes:
   - Parses measurements and symptoms
   - Matches against knowledge base patterns
   - Diagnoses suspected faults
   - Generates recommendations
4. Response sent back with case_id and recommendations
5. Case stored in memory for future reference
```

### Learning Flow
```
1. Technician/robot performs repair actions
2. iaRealidad reports outcome to /technical/outcome
3. TechnicalMemoryStore:
   - Stores outcome linked to case
   - Updates fault patterns
   - Recalculates success rates
   - Learns common symptom-action pairs
4. Knowledge base improves incrementally
```

## Knowledge Base

The system maintains symbolic knowledge about electronics repair:

### Voltage Patterns
- **Low Voltage** (< 80% expected): Suggests power supply issues
- **No Voltage** (< 10% expected): Suggests shorts or disconnections
- **High Voltage** (> 120% expected): Suggests regulator issues

### Board-Specific Knowledge
Each board type has:
- Critical voltage points
- Common failure modes
- Typical diagnostic procedures

### Pattern Learning
The system learns patterns from outcomes:
- Which actions work for which faults
- Success rates by board type
- Time and cost estimates
- Common symptom combinations

## Benefits

### For iaRealidad Integration
1. **Structured Input**: Clear API for sending measurements and events
2. **Intelligent Diagnosis**: Symbolic reasoning about electronics
3. **Historical Context**: Leverage past cases for better decisions
4. **Continuous Learning**: System improves with each repair
5. **Quantified Confidence**: Know how reliable each diagnosis is

### For Operational AI
1. **Memory**: Persistent storage of technical cases
2. **Pattern Recognition**: Learns common fault patterns
3. **Success Tracking**: Knows what works and what doesn't
4. **Adaptability**: Improves over time without retraining
5. **Explainability**: Clear reasoning for recommendations

## Future Enhancements

- Real-time feedback during repair process
- Computer vision integration for visual inspection
- Multi-step repair planning
- Cost optimization for repair decisions
- Predictive maintenance based on patterns
- Integration with parts inventory systems

## Summary

The Electronics Repair Domain transforms BlackMamba Cognitive Core into an operational AI for electronics repair. Combined with iaRealidad's sensing and actuation capabilities, it creates a complete system that can:

**Sense → Diagnose → Act → Remember → Improve**

This is not a conversational AI—it's an **operational AI** that actively participates in technical work, learns from experience, and gets better over time.
