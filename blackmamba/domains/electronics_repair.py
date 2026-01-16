"""
Electronics Repair Domain Processor

This domain specializes in:
- Processing technical measurements and events
- Diagnosing electronic board failures
- Recommending repair actions
- Learning from repair outcomes
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone

from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import Input, ProcessingContext, Response, InputType
from blackmamba.core.technical_types import (
    BoardType,
    FaultType,
    MeasurementType,
    Measurement,
    Symptom,
    DiagnosticCase,
    RepairAction,
    RepairActionType,
    OutcomeStatus,
)


class ElectronicsRepairDomain(DomainProcessor):
    """
    Domain processor for electronics repair and diagnostics
    
    Handles:
    - Technical measurements (voltage, current, etc.)
    - Symptom analysis
    - Fault diagnosis
    - Repair recommendations
    """
    
    def __init__(self):
        self._knowledge_base = self._initialize_knowledge_base()
    
    @property
    def domain_name(self) -> str:
        return "electronics_repair"
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """
        Initialize knowledge base with common patterns
        
        This represents symbolic knowledge about electronics repair
        """
        return {
            "voltage_patterns": {
                "low_voltage": {
                    "threshold": 0.9,  # 90% of expected
                    "likely_faults": [FaultType.LOW_VOLTAGE, FaultType.NO_POWER],
                    "actions": [
                        RepairActionType.CHECK_CONNECTION,
                        RepairActionType.REPLACE_POWER_SUPPLY,
                        RepairActionType.REPLACE_COMPONENT
                    ]
                },
                "no_voltage": {
                    "threshold": 0.1,  # 10% of expected
                    "likely_faults": [FaultType.NO_POWER, FaultType.SHORT_CIRCUIT],
                    "actions": [
                        RepairActionType.CHECK_CONNECTION,
                        RepairActionType.REPLACE_POWER_SUPPLY,
                        RepairActionType.RESOLDER
                    ]
                },
                "high_voltage": {
                    "threshold": 1.1,  # 110% of expected
                    "likely_faults": [FaultType.HIGH_VOLTAGE],
                    "actions": [
                        RepairActionType.ADJUST_VOLTAGE,
                        RepairActionType.REPLACE_COMPONENT
                    ]
                }
            },
            "symptom_patterns": {
                "no boot": [FaultType.NO_BOOT, FaultType.CORRUPTED_FIRMWARE],
                "no arranca": [FaultType.NO_BOOT, FaultType.CORRUPTED_FIRMWARE],
                "not booting": [FaultType.NO_BOOT],
                "no power": [FaultType.NO_POWER],
                "sin energía": [FaultType.NO_POWER],
                "no communication": [FaultType.NO_COMMUNICATION],
                "sin comunicación": [FaultType.NO_COMMUNICATION],
                "overheating": [FaultType.OVERHEATING],
                "sobrecalentamiento": [FaultType.OVERHEATING],
                "caliente": [FaultType.OVERHEATING],
            },
            "board_specific": {
                BoardType.ESP32: {
                    "critical_voltages": {
                        "VCC": {"expected": 3.3, "unit": "V"},
                        "3V3": {"expected": 3.3, "unit": "V"},
                        "5V": {"expected": 5.0, "unit": "V"},
                    },
                    "common_issues": [FaultType.NO_BOOT, FaultType.NO_COMMUNICATION]
                },
                BoardType.ARDUINO: {
                    "critical_voltages": {
                        "5V": {"expected": 5.0, "unit": "V"},
                        "3V3": {"expected": 3.3, "unit": "V"},
                    },
                    "common_issues": [FaultType.NO_BOOT, FaultType.CORRUPTED_FIRMWARE]
                }
            }
        }
    
    async def can_handle(self, input_data: Input, context: ProcessingContext) -> bool:
        """
        Determine if this is a technical/repair-related input
        """
        if input_data.type == InputType.EVENT:
            event_type = input_data.content.get("event_type", "")
            # Check if it's a technical event
            technical_types = [
                "measurement", "diagnosis", "symptom", "repair",
                "technical_event", "board_event", "sensor_reading"
            ]
            return any(tech_type in event_type.lower() for tech_type in technical_types)
        
        if input_data.type == InputType.TEXT:
            text_content = input_data.content.get("text", "").lower()
            # Check for technical keywords
            technical_keywords = [
                "voltage", "current", "board", "esp32", "arduino",
                "no arranca", "not booting", "measurement", "repair",
                "diagnóstico", "falla", "fault", "circuit", "sensor"
            ]
            return any(keyword in text_content for keyword in technical_keywords)
        
        return False
    
    async def analyze(self, input_data: Input, context: ProcessingContext) -> Dict[str, Any]:
        """
        Analyze technical input and extract diagnostic information
        """
        analysis = {
            "measurements": [],
            "symptoms": [],
            "board_type": BoardType.UNKNOWN,
            "suspected_faults": [],
            "confidence": 0.0,
            "patterns_matched": []
        }
        
        if input_data.type == InputType.EVENT:
            analysis = await self._analyze_event(input_data, analysis)
        elif input_data.type == InputType.TEXT:
            analysis = await self._analyze_text(input_data, analysis)
        
        # Diagnose based on analysis
        analysis = await self._diagnose(analysis)
        
        return analysis
    
    async def _analyze_event(self, input_data: Input, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical event"""
        event_content = input_data.content
        event_type = event_content.get("event_type", "")
        # Get the actual event data (it's nested under "data" key)
        event_data = event_content.get("data", event_content)
        
        # Extract board type
        board_str = event_data.get("board", event_data.get("board_type", ""))
        analysis["board_type"] = self._parse_board_type(board_str)
        
        # Check if this is a measurement event
        if "measurement" in event_type.lower():
            measurement = self._extract_measurement(event_data)
            if measurement:
                analysis["measurements"].append(measurement)
        
        # Check for symptom or diagnostic data
        if "symptom" in event_type.lower() or "issue" in event_type.lower():
            symptom = self._extract_symptom(event_data)
            if symptom:
                analysis["symptoms"].append(symptom)
        
        # Look for structured measurement data
        if "value" in event_data and "expected" in event_data:
            measurement = Measurement(
                type=MeasurementType.VOLTAGE,  # Default, could be inferred
                value=float(event_data["value"]),
                unit=event_data.get("unit", "V"),
                expected_value=float(event_data["expected"]),
                expected_unit=event_data.get("unit", "V"),
                location=event_data.get("location", "unknown")
            )
            analysis["measurements"].append(measurement)
        
        return analysis
    
    async def _analyze_text(self, input_data: Input, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text description of technical issue"""
        text = input_data.content.get("text", "").lower()
        
        # Extract board type from text
        for board_type in BoardType:
            if board_type.value.lower() in text:
                analysis["board_type"] = board_type
                break
        
        # Match symptom patterns
        for symptom_text, faults in self._knowledge_base["symptom_patterns"].items():
            if symptom_text in text:
                symptom = Symptom(
                    description=symptom_text,
                    severity=3,
                    context={"source": "text_analysis"}
                )
                analysis["symptoms"].append(symptom)
                analysis["suspected_faults"].extend(faults)
                analysis["patterns_matched"].append(symptom_text)
        
        return analysis
    
    def _parse_board_type(self, board_str: str) -> BoardType:
        """Parse board type from string"""
        board_str_lower = board_str.lower()
        for board_type in BoardType:
            if board_type.value.lower() in board_str_lower:
                return board_type
        return BoardType.UNKNOWN
    
    def _extract_measurement(self, data: Dict[str, Any]) -> Optional[Measurement]:
        """Extract measurement from event data"""
        try:
            meas_type = data.get("measurement_type", "voltage")
            # Handle both "expected" and "expected_value" keys
            expected_val = data.get("expected_value") or data.get("expected")
            return Measurement(
                type=MeasurementType(meas_type) if meas_type in [m.value for m in MeasurementType] else MeasurementType.VOLTAGE,
                value=float(data.get("value", 0)),
                unit=data.get("unit", "V"),
                expected_value=float(expected_val) if expected_val else None,
                location=data.get("location", "unknown")
            )
        except (ValueError, KeyError):
            return None
    
    def _extract_symptom(self, data: Dict[str, Any]) -> Optional[Symptom]:
        """Extract symptom from event data"""
        description = data.get("description", data.get("symptom", ""))
        if description:
            return Symptom(
                description=description,
                severity=data.get("severity", 3),
                context=data.get("context", {})
            )
        return None
    
    async def _diagnose(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform diagnosis based on measurements and symptoms
        """
        suspected_faults = set(analysis["suspected_faults"])
        confidence = 0.0
        
        # Analyze measurements
        for measurement in analysis["measurements"]:
            if isinstance(measurement, dict):
                # Convert dict to Measurement object if needed
                try:
                    measurement = Measurement(**measurement)
                except (TypeError, ValueError) as e:
                    # Skip invalid measurements but log the issue
                    import logging
                    logging.warning(f"Failed to process measurement: {e}")
                    continue
            
            if measurement.expected_value:
                ratio = measurement.value / measurement.expected_value if measurement.expected_value > 0 else 0
                
                # Check voltage patterns
                if measurement.type == MeasurementType.VOLTAGE:
                    if ratio < 0.1:
                        suspected_faults.update([FaultType.NO_POWER, FaultType.SHORT_CIRCUIT])
                        confidence = max(confidence, 0.8)
                    elif ratio < 0.9:
                        suspected_faults.update([FaultType.LOW_VOLTAGE, FaultType.NO_POWER])
                        confidence = max(confidence, 0.7)
                    elif ratio > 1.1:
                        suspected_faults.add(FaultType.HIGH_VOLTAGE)
                        confidence = max(confidence, 0.6)
        
        # Boost confidence if we have symptoms matching
        if analysis["symptoms"]:
            confidence = max(confidence, 0.6)
        
        # If we have both measurements and symptoms, higher confidence
        if analysis["measurements"] and analysis["symptoms"]:
            confidence = min(1.0, confidence + 0.2)
        
        analysis["suspected_faults"] = list(suspected_faults)
        analysis["confidence"] = confidence
        
        return analysis
    
    async def synthesize(
        self, input_data: Input, context: ProcessingContext, analysis_results: Dict[str, Any]
    ) -> Response:
        """
        Generate diagnostic response and repair recommendations
        """
        # Create diagnostic case
        case = DiagnosticCase(
            id=str(uuid.uuid4()),
            board_type=analysis_results.get("board_type", BoardType.UNKNOWN),
            symptoms=[s if isinstance(s, Symptom) else Symptom(**s) for s in analysis_results.get("symptoms", [])],
            measurements=[m if isinstance(m, Measurement) else Measurement(**m) for m in analysis_results.get("measurements", [])],
            suspected_faults=analysis_results.get("suspected_faults", []),
            confidence=analysis_results.get("confidence", 0.0)
        )
        
        # Generate repair recommendations
        recommendations = self._generate_recommendations(case, analysis_results)
        
        # Build response content
        response_content = {
            "case_id": case.id,
            "board_type": case.board_type.value,
            "diagnosis": {
                "suspected_faults": [f.value for f in case.suspected_faults],
                "confidence": case.confidence,
                "measurements_summary": self._summarize_measurements(case.measurements),
                "symptoms_summary": [s.description for s in case.symptoms]
            },
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(case, recommendations)
        }
        
        response = Response(
            id=str(uuid.uuid4()),
            input_id=input_data.id,
            content=response_content,
            confidence=case.confidence,
            metadata={
                "domain": self.domain_name,
                "case_id": case.id,
                "patterns_matched": analysis_results.get("patterns_matched", [])
            }
        )
        
        return response
    
    def _generate_recommendations(self, case: DiagnosticCase, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate repair action recommendations"""
        recommendations = []
        
        # Get actions from knowledge base based on faults
        for fault in case.suspected_faults:
            # Check voltage patterns
            for pattern_name, pattern in self._knowledge_base["voltage_patterns"].items():
                if fault in pattern.get("likely_faults", []):
                    for action_type in pattern["actions"]:
                        recommendations.append({
                            "action": action_type.value,
                            "reason": f"Common fix for {fault.value}",
                            "priority": "high" if case.confidence > 0.7 else "medium"
                        })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            rec_key = rec["action"]
            if rec_key not in seen:
                seen.add(rec_key)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Top 5 recommendations
    
    def _summarize_measurements(self, measurements: List[Measurement]) -> List[Dict[str, Any]]:
        """Summarize measurements for response"""
        summary = []
        for m in measurements:
            item = {
                "type": m.type.value,
                "value": m.value,
                "unit": m.unit,
                "location": m.location
            }
            if m.expected_value:
                item["expected"] = m.expected_value
                item["out_of_range"] = m.is_out_of_range()
            summary.append(item)
        return summary
    
    def _generate_next_steps(self, case: DiagnosticCase, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate human-readable next steps"""
        steps = []
        
        if case.confidence < 0.5:
            steps.append("Gather more diagnostic data (additional measurements or symptoms)")
        
        if case.measurements:
            steps.append("Verify all measurements are accurate")
        
        if recommendations:
            steps.append(f"Start with: {recommendations[0]['action'].replace('_', ' ')}")
        
        if case.board_type != BoardType.UNKNOWN:
            steps.append(f"Review {case.board_type.value} specific documentation")
        
        steps.append("Document outcome for learning")
        
        return steps
