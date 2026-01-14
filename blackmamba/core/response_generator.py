"""
Response generator - Creates intelligent responses
"""
import uuid
from typing import Dict, Any
from datetime import datetime
from blackmamba.core.types import Response, ProcessingContext


class ResponseGenerator:
    """Generates intelligent responses based on processing results"""
    
    def __init__(self):
        self._response_strategies = {}
    
    async def generate(
        self,
        input_id: str,
        context: ProcessingContext,
        synthesis_data: Dict[str, Any],
        confidence: float = 0.8
    ) -> Response:
        """
        Generate a response from synthesis data
        
        Args:
            input_id: ID of the input being responded to
            context: Processing context
            synthesis_data: Data from synthesis phase
            confidence: Confidence score for the response
            
        Returns:
            Generated Response object
        """
        response_content = await self._build_response_content(
            synthesis_data,
            context
        )
        
        return Response(
            id=str(uuid.uuid4()),
            input_id=input_id,
            content=response_content,
            confidence=min(max(confidence, 0.0), 1.0),
            metadata={
                "domain": context.domain,
                "stage": context.stage.value,
                "memory_refs": context.memory_refs,
            },
            timestamp=datetime.utcnow()
        )
    
    async def _build_response_content(
        self,
        synthesis_data: Dict[str, Any],
        context: ProcessingContext
    ) -> Dict[str, Any]:
        """
        Build the response content structure
        
        Args:
            synthesis_data: Synthesis results
            context: Processing context
            
        Returns:
            Structured response content
        """
        content = {
            "type": "response",
            "data": synthesis_data.get("response_data", {}),
            "summary": synthesis_data.get("summary", ""),
        }
        
        # Add domain-specific enhancements
        if context.domain:
            content["domain"] = context.domain
            
        # Add analysis insights if available
        if context.analysis_results:
            content["insights"] = self._extract_insights(context.analysis_results)
        
        return content
    
    def _extract_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from analysis results"""
        insights = {}
        
        # Extract key metrics
        if "metrics" in analysis_results:
            insights["metrics"] = analysis_results["metrics"]
        
        # Extract patterns
        if "patterns" in analysis_results:
            insights["patterns"] = analysis_results["patterns"]
        
        # Extract recommendations
        if "recommendations" in analysis_results:
            insights["recommendations"] = analysis_results["recommendations"]
        
        return insights
    
    def register_strategy(self, domain: str, strategy_func):
        """Register a custom response strategy for a domain"""
        self._response_strategies[domain] = strategy_func
