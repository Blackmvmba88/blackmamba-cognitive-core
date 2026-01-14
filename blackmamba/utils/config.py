"""
Configuration management utilities
"""
import os
from typing import Optional
from pydantic import BaseModel


class CognitiveConfig(BaseModel):
    """Configuration for the cognitive system"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Memory Configuration
    memory_persist_path: Optional[str] = "./data/memory.json"
    memory_enabled: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Processing Configuration
    max_text_length: int = 10000
    max_audio_size_mb: int = 10
    
    @classmethod
    def from_env(cls) -> "CognitiveConfig":
        """Load configuration from environment variables"""
        return cls(
            api_host=os.getenv("COGNITIVE_API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("COGNITIVE_API_PORT", "8000")),
            api_reload=os.getenv("COGNITIVE_API_RELOAD", "false").lower() == "true",
            memory_persist_path=os.getenv("COGNITIVE_MEMORY_PATH", "./data/memory.json"),
            memory_enabled=os.getenv("COGNITIVE_MEMORY_ENABLED", "true").lower() == "true",
            log_level=os.getenv("COGNITIVE_LOG_LEVEL", "INFO"),
            max_text_length=int(os.getenv("COGNITIVE_MAX_TEXT_LENGTH", "10000")),
            max_audio_size_mb=int(os.getenv("COGNITIVE_MAX_AUDIO_SIZE_MB", "10")),
        )


# Global config instance
config = CognitiveConfig.from_env()
