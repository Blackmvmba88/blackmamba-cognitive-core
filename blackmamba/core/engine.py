"""
Cognitive Engine - Main orchestrator for the cognitive system

This module provides the main cognitive engine with support for both
legacy domain registration and new registry-based architecture.
"""

from typing import List, Optional, Dict, Any, Union
import logging
from blackmamba.core.types import Input, ProcessingContext, Response, ProcessingStage
from blackmamba.core.interfaces import DomainProcessor, MemoryStore
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.response_generator import ResponseGenerator


logger = logging.getLogger(__name__)


class CognitiveEngine:
    """
    Main cognitive engine that orchestrates input processing,
    domain coordination, analysis, and response generation
    
    Supports both legacy mode (simple list of domains) and new mode
    (registry + router) for backward compatibility.
    """

    def __init__(
        self,
        input_processor: Optional[InputProcessor] = None,
        response_generator: Optional[ResponseGenerator] = None,
        memory_store: Optional[MemoryStore] = None,
        use_registry: bool = False,
    ):
        """
        Initialize the cognitive engine

        Args:
            input_processor: Input processor instance
            response_generator: Response generator instance
            memory_store: Memory store instance
            use_registry: If True, use new DomainRegistry + Router architecture
        """
        self.input_processor = input_processor or InputProcessor()
        self.response_generator = response_generator or ResponseGenerator()
        self.memory_store = memory_store
        
        # Legacy mode (backward compatible)
        self.domain_processors: List[DomainProcessor] = []
        
        # New registry mode (opt-in for now)
        self._use_registry = use_registry
        self._registry = None
        self._router = None
        
        if use_registry:
            # Lazy import to avoid circular dependencies
            from blackmamba.core.domain_registry import DomainRegistry
            from blackmamba.core.domain_router import DomainRouter
            
            self._registry = DomainRegistry()
            self._router = DomainRouter(self._registry)
            logger.info("CognitiveEngine initialized with DomainRegistry")
        else:
            logger.info("CognitiveEngine initialized (legacy mode)")

    def register_domain_processor(
        self, 
        processor: DomainProcessor,
        priority: int = 0,
        version: str = "1.0.0",
    ):
        """
        Register a domain processor
        
        In legacy mode, adds to simple list. In registry mode, registers
        with the DomainRegistry for advanced features.

        Args:
            processor: Domain processor to register
            priority: Priority for routing (registry mode only)
            version: Domain version (registry mode only)
        """
        if self._use_registry and self._registry:
            # Use new registry
            self._registry.register(
                processor=processor,
                version=version,
                priority=priority,
            )
        else:
            # Legacy mode
            self.domain_processors.append(processor)
        
        logger.info(f"Registered domain processor: {processor.domain_name}")

    async def process(self, input_data: Input) -> Response:
        """
        Process an input through the cognitive pipeline

        Args:
            input_data: Input to process

        Returns:
            Generated response
        """
        # Validate input
        if not await self.input_processor.validate_input(input_data):
            raise ValueError(f"Invalid input: {input_data.id}")

        # Create processing context
        context = ProcessingContext(input_id=input_data.id, stage=ProcessingStage.RECEIVED)

        logger.info(f"Processing input {input_data.id} of type {input_data.type}")

        try:
            # Find appropriate domain processor
            processor = await self._select_domain_processor(input_data, context)

            if processor:
                context.domain = processor.domain_name
                logger.info(f"Selected domain processor: {processor.domain_name}")

            # Analysis phase
            context.stage = ProcessingStage.ANALYZING
            analysis_results = await self._analyze(input_data, context, processor)
            context.analysis_results = analysis_results

            # Store in memory if available
            if self.memory_store:
                memory_id = await self.memory_store.store(
                    key=f"input_{input_data.id}",
                    value={"input": input_data.model_dump(), "analysis": analysis_results},
                    tags=(
                        [input_data.type.value, context.domain]
                        if context.domain
                        else [input_data.type.value]
                    ),
                )
                context.memory_refs.append(memory_id)

            # Synthesis phase
            context.stage = ProcessingStage.SYNTHESIZING
            response = await self._synthesize(input_data, context, analysis_results, processor)

            # Mark as completed
            context.stage = ProcessingStage.COMPLETED
            logger.info(f"Successfully processed input {input_data.id}")

            return response

        except Exception as e:
            context.stage = ProcessingStage.FAILED
            logger.error(f"Failed to process input {input_data.id}: {str(e)}")
            raise

    async def _select_domain_processor(
        self, input_data: Input, context: ProcessingContext
    ) -> Optional[DomainProcessor]:
        """
        Select the most appropriate domain processor
        
        Uses intelligent routing in registry mode, simple iteration in legacy mode.
        """
        if self._use_registry and self._router:
            # Use intelligent router
            result = await self._router.route(input_data, context)
            if result:
                domain_name, processor, score = result
                logger.debug(f"Router selected {domain_name} (score={score.score:.2f})")
                
                # Record success for circuit breaker
                self._router.record_success(domain_name)
                
                return processor
            return None
        else:
            # Legacy mode: simple iteration
            for processor in self.domain_processors:
                if await processor.can_handle(input_data, context):
                    return processor
            return None

    async def _analyze(
        self, input_data: Input, context: ProcessingContext, processor: Optional[DomainProcessor]
    ) -> Dict[str, Any]:
        """Run analysis phase"""
        if processor:
            return await processor.analyze(input_data, context)

        # Default analysis if no domain processor
        return {
            "type": input_data.type.value,
            "content_keys": list(input_data.content.keys()),
            "metadata_keys": list(input_data.metadata.keys()),
        }

    async def _synthesize(
        self,
        input_data: Input,
        context: ProcessingContext,
        analysis_results: Dict[str, Any],
        processor: Optional[DomainProcessor],
    ) -> Response:
        """Run synthesis phase"""
        if processor:
            return await processor.synthesize(input_data, context, analysis_results)

        # Default synthesis if no domain processor
        synthesis_data = {
            "response_data": {
                "message": "Input received and analyzed",
                "input_id": input_data.id,
                "type": input_data.type.value,
            },
            "summary": f"Processed {input_data.type.value} input successfully",
        }

        return await self.response_generator.generate(
            input_id=input_data.id, context=context, synthesis_data=synthesis_data, confidence=0.7
        )

    async def get_memory_context(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memory context

        Args:
            tags: Tags to search for

        Returns:
            List of relevant memory entries
        """
        if not self.memory_store:
            return []

        return await self.memory_store.search({"tags": tags})
    
    # New registry-specific methods
    
    @property
    def registry(self):
        """Get the domain registry (registry mode only)"""
        if not self._use_registry:
            raise RuntimeError("Registry not available in legacy mode. Initialize with use_registry=True")
        return self._registry
    
    @property
    def router(self):
        """Get the domain router (registry mode only)"""
        if not self._use_registry:
            raise RuntimeError("Router not available in legacy mode. Initialize with use_registry=True")
        return self._router
    
    def get_domain_stats(self) -> Dict[str, Any]:
        """
        Get statistics about registered domains
        
        Returns:
            Dictionary with domain statistics
        """
        if self._use_registry and self._registry:
            return {
                "mode": "registry",
                "registry": self._registry.get_stats(),
                "router": self._router.get_stats() if self._router else {},
            }
        else:
            return {
                "mode": "legacy",
                "total_domains": len(self.domain_processors),
                "domains": [p.domain_name for p in self.domain_processors],
            }
    
    async def health_check_domains(self) -> Dict[str, Any]:
        """
        Perform health check on all domains
        
        Returns:
            Dictionary with health status per domain
        """
        if self._use_registry and self._registry:
            return await self._registry.health_check_all()
        else:
            # Legacy mode: basic check
            results = {}
            for processor in self.domain_processors:
                try:
                    if hasattr(processor, 'health_check'):
                        is_healthy = await processor.health_check()
                        results[processor.domain_name] = "healthy" if is_healthy else "unhealthy"
                    else:
                        results[processor.domain_name] = "unknown"
                except Exception as e:
                    logger.error(f"Health check failed for {processor.domain_name}: {e}")
                    results[processor.domain_name] = "unhealthy"
            return results
