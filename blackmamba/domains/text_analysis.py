"""
Text analysis domain processor
"""
from typing import Dict, Any
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import Input, ProcessingContext, Response, InputType
from blackmamba.core.response_generator import ResponseGenerator


class TextAnalysisDomain(DomainProcessor):
    """Domain processor for text analysis tasks"""
    
    def __init__(self):
        self._response_gen = ResponseGenerator()
    
    @property
    def domain_name(self) -> str:
        return "text_analysis"
    
    async def can_handle(self, input_data: Input, context: ProcessingContext) -> bool:
        """Check if this processor can handle the input"""
        return input_data.type == InputType.TEXT
    
    async def analyze(self, input_data: Input, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze text input"""
        text = input_data.content.get("text", "")
        
        # Perform basic text analysis
        words = text.split()
        sentences = text.split('.')
        
        analysis = {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "character_count": len(text),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "unique_words": len(set(words)),
            "metrics": {
                "complexity": self._calculate_complexity(text),
                "sentiment_hint": self._basic_sentiment(text),
            },
            "patterns": self._detect_patterns(text),
        }
        
        return analysis
    
    async def synthesize(
        self,
        input_data: Input,
        context: ProcessingContext,
        analysis_results: Dict[str, Any]
    ) -> Response:
        """Synthesize response from text analysis"""
        text = input_data.content.get("text", "")
        
        # Generate insights
        insights = []
        if analysis_results["word_count"] > 100:
            insights.append("Este es un texto largo con contenido sustancial")
        if analysis_results["metrics"]["complexity"] > 0.7:
            insights.append("El texto tiene alta complejidad lingüística")
        
        synthesis_data = {
            "response_data": {
                "message": "Análisis de texto completado",
                "word_count": analysis_results["word_count"],
                "complexity": analysis_results["metrics"]["complexity"],
                "insights": insights,
            },
            "summary": f"Analizado texto de {analysis_results['word_count']} palabras",
        }
        
        return await self._response_gen.generate(
            input_id=input_data.id,
            context=context,
            synthesis_data=synthesis_data,
            confidence=0.85
        )
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1)"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        # Simple complexity based on average word length
        avg_length = sum(len(w) for w in words) / len(words)
        complexity = min(avg_length / 15, 1.0)  # Normalize to 0-1
        
        return round(complexity, 2)
    
    def _basic_sentiment(self, text: str) -> str:
        """Basic sentiment detection"""
        text_lower = text.lower()
        
        positive_words = ["bueno", "excelente", "feliz", "alegre", "positivo", "bien"]
        negative_words = ["malo", "triste", "negativo", "mal", "terrible"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def _detect_patterns(self, text: str) -> Dict[str, Any]:
        """Detect patterns in text"""
        patterns = {}
        
        # Detect questions
        patterns["questions"] = text.count("?")
        
        # Detect exclamations
        patterns["exclamations"] = text.count("!")
        
        # Detect numbers
        patterns["has_numbers"] = any(char.isdigit() for char in text)
        
        return patterns
