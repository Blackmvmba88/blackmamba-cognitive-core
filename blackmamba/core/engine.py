"""
Cognitive Engine - Main orchestrator for the cognitive system
"""

from typing import List, Optional, Dict, Any
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
    """

    def __init__(
        self,
        input_processor: Optional[InputProcessor] = None,
        response_generator: Optional[ResponseGenerator] = None,
        memory_store: Optional[MemoryStore] = None,
    ):
        """
        Initialize the cognitive engine

        Args:
            input_processor: Input processor instance
            response_generator: Response generator instance
            memory_store: Memory store instance
        """
        self.input_processor = input_processor or InputProcessor()
        self.response_generator = response_generator or ResponseGenerator()
        self.memory_store = memory_store
        self.domain_processors: List[DomainProcessor] = []

        logger.info("CognitiveEngine initialized")

    def register_domain_processor(self, processor: DomainProcessor):
        """
        Register a domain processor

        Args:
            processor: Domain processor to register
        """
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
        """Select the most appropriate domain processor"""
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
