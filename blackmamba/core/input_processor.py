"""
Input processor - Handles diverse input types (text, audio, events)
"""

import uuid
from typing import Dict, Any
from datetime import datetime, timezone
from blackmamba.core.types import Input, InputType


class InputProcessor:
    """Processes and normalizes diverse input types"""

    def __init__(self):
        self._validators = {
            InputType.TEXT: self._validate_text,
            InputType.AUDIO: self._validate_audio,
            InputType.EVENT: self._validate_event,
        }

    async def process_text(self, text: str, metadata: Dict[str, Any] = None) -> Input:
        """
        Process text input

        Args:
            text: The text content
            metadata: Optional metadata

        Returns:
            Normalized Input object
        """
        return Input(
            id=str(uuid.uuid4()),
            type=InputType.TEXT,
            content={"text": text, "length": len(text)},
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )

    async def process_audio(
        self, audio_data: bytes, format: str = "wav", metadata: Dict[str, Any] = None
    ) -> Input:
        """
        Process audio input

        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, etc.)
            metadata: Optional metadata

        Returns:
            Normalized Input object
        """
        return Input(
            id=str(uuid.uuid4()),
            type=InputType.AUDIO,
            content={
                "format": format,
                "size_bytes": len(audio_data),
                "data_preview": audio_data[:100].hex() if audio_data else "",
            },
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )

    async def process_event(
        self, event_type: str, event_data: Dict[str, Any], metadata: Dict[str, Any] = None
    ) -> Input:
        """
        Process event input

        Args:
            event_type: Type of event
            event_data: Event data
            metadata: Optional metadata

        Returns:
            Normalized Input object
        """
        return Input(
            id=str(uuid.uuid4()),
            type=InputType.EVENT,
            content={
                "event_type": event_type,
                "data": event_data,
            },
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )

    async def validate_input(self, input_data: Input) -> bool:
        """
        Validate an input object

        Args:
            input_data: The input to validate

        Returns:
            True if valid, False otherwise
        """
        if input_data.type not in self._validators:
            return False

        return self._validators[input_data.type](input_data)

    def _validate_text(self, input_data: Input) -> bool:
        """Validate text input"""
        return "text" in input_data.content and isinstance(input_data.content["text"], str)

    def _validate_audio(self, input_data: Input) -> bool:
        """Validate audio input"""
        return "format" in input_data.content and "size_bytes" in input_data.content

    def _validate_event(self, input_data: Input) -> bool:
        """Validate event input"""
        return "event_type" in input_data.content and "data" in input_data.content
