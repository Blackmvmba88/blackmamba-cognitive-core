"""
Event processing domain processor
"""

from typing import Dict, Any
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import Input, ProcessingContext, Response, InputType
from blackmamba.core.response_generator import ResponseGenerator


class EventProcessingDomain(DomainProcessor):
    """Domain processor for event processing tasks"""

    def __init__(self):
        self._response_gen = ResponseGenerator()
        self._event_history = []

    @property
    def domain_name(self) -> str:
        return "event_processing"

    async def can_handle(self, input_data: Input, context: ProcessingContext) -> bool:
        """Check if this processor can handle the input"""
        return input_data.type == InputType.EVENT

    async def analyze(self, input_data: Input, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze event input"""
        event_type = input_data.content.get("event_type", "unknown")
        event_data = input_data.content.get("data", {})

        # Record event in history
        self._event_history.append(
            {"id": input_data.id, "type": event_type, "timestamp": input_data.timestamp}
        )

        # Analyze event
        analysis = {
            "event_type": event_type,
            "data_fields": list(event_data.keys()),
            "data_size": len(str(event_data)),
            "timestamp": input_data.timestamp.isoformat(),
            "metrics": {
                "priority": self._calculate_priority(event_type, event_data),
                "requires_action": self._requires_action(event_type, event_data),
            },
            "patterns": {
                "recent_similar_events": self._count_similar_events(event_type),
                "event_frequency": len(self._event_history),
            },
            "recommendations": self._generate_recommendations(event_type, event_data),
        }

        return analysis

    async def synthesize(
        self, input_data: Input, context: ProcessingContext, analysis_results: Dict[str, Any]
    ) -> Response:
        """Synthesize response from event analysis"""
        event_type = analysis_results["event_type"]

        response_message = f"Evento '{event_type}' procesado exitosamente"

        # Add action items if needed
        actions = []
        if analysis_results["metrics"]["requires_action"]:
            actions.append(f"Requiere atención: {event_type}")

        if analysis_results["patterns"]["recent_similar_events"] > 3:
            actions.append("Patrón detectado: eventos similares frecuentes")

        synthesis_data = {
            "response_data": {
                "message": response_message,
                "event_type": event_type,
                "priority": analysis_results["metrics"]["priority"],
                "actions": actions,
                "recommendations": analysis_results.get("recommendations", []),
            },
            "summary": (
                f"Evento {event_type} analizado con prioridad "
                f"{analysis_results['metrics']['priority']}"
            ),
        }

        confidence = (
            0.9 if analysis_results["metrics"]["priority"] in ["high", "critical"] else 0.75
        )

        return await self._response_gen.generate(
            input_id=input_data.id,
            context=context,
            synthesis_data=synthesis_data,
            confidence=confidence,
        )

    def _calculate_priority(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Calculate event priority"""
        priority_keywords = {
            "critical": ["error", "critical", "failure", "crash"],
            "high": ["warning", "alert", "urgent"],
            "medium": ["info", "update", "change"],
            "low": ["debug", "trace", "log"],
        }

        event_type_lower = event_type.lower()

        for priority, keywords in priority_keywords.items():
            if any(keyword in event_type_lower for keyword in keywords):
                return priority

        return "medium"

    def _requires_action(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Determine if event requires action"""
        priority = self._calculate_priority(event_type, event_data)
        return priority in ["critical", "high"]

    def _count_similar_events(self, event_type: str, lookback: int = 10) -> int:
        """Count similar events in recent history"""
        recent_events = self._event_history[-lookback:]
        return sum(1 for e in recent_events if e["type"] == event_type)

    def _generate_recommendations(self, event_type: str, event_data: Dict[str, Any]) -> list:
        """Generate recommendations based on event"""
        recommendations = []

        priority = self._calculate_priority(event_type, event_data)

        if priority == "critical":
            recommendations.append("Revisar logs del sistema inmediatamente")
            recommendations.append("Notificar al equipo de respuesta")
        elif priority == "high":
            recommendations.append("Investigar causa del evento")

        similar_count = self._count_similar_events(event_type)
        if similar_count > 5:
            recommendations.append("Considerar automatización para eventos recurrentes")

        return recommendations
