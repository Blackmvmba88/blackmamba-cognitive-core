"""
Base interfaces for domain processors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from blackmamba.core.types import Input, ProcessingContext, Response


class DomainProcessor(ABC):
    """Base interface for domain-specific processors"""

    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Return the name of this domain"""
        pass

    @abstractmethod
    async def can_handle(self, input_data: Input, context: ProcessingContext) -> bool:
        """
        Determine if this processor can handle the given input

        Args:
            input_data: The input to check
            context: Current processing context

        Returns:
            True if this processor can handle the input
        """
        pass

    @abstractmethod
    async def analyze(self, input_data: Input, context: ProcessingContext) -> Dict[str, Any]:
        """
        Analyze the input and return analysis results

        Args:
            input_data: The input to analyze
            context: Current processing context

        Returns:
            Dictionary containing analysis results
        """
        pass

    @abstractmethod
    async def synthesize(
        self, input_data: Input, context: ProcessingContext, analysis_results: Dict[str, Any]
    ) -> Response:
        """
        Synthesize a response based on analysis

        Args:
            input_data: The original input
            context: Current processing context
            analysis_results: Results from the analysis phase

        Returns:
            Generated response
        """
        pass


class MemoryStore(ABC):
    """Base interface for memory storage"""

    @abstractmethod
    async def store(self, key: str, value: Dict[str, Any], tags: Optional[list] = None) -> str:
        """Store a value in memory"""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a value from memory"""
        pass

    @abstractmethod
    async def search(self, query: Dict[str, Any]) -> list:
        """Search memory with a query"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from memory"""
        pass
