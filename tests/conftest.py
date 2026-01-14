"""Test configuration and fixtures"""
import pytest
import os
import tempfile
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.response_generator import ResponseGenerator
from blackmamba.memory.store import InMemoryStore
from blackmamba.domains.text_analysis import TextAnalysisDomain
from blackmamba.domains.event_processing import EventProcessingDomain


@pytest.fixture
def temp_memory_path():
    """Create a temporary file path for memory storage"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        path = f.name
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def memory_store(temp_memory_path):
    """Create a memory store instance"""
    return InMemoryStore(persist_path=temp_memory_path)


@pytest.fixture
def input_processor():
    """Create an input processor instance"""
    return InputProcessor()


@pytest.fixture
def response_generator():
    """Create a response generator instance"""
    return ResponseGenerator()


@pytest.fixture
def cognitive_engine(input_processor, response_generator, memory_store):
    """Create a cognitive engine instance"""
    engine = CognitiveEngine(
        input_processor=input_processor,
        response_generator=response_generator,
        memory_store=memory_store
    )
    
    # Register domain processors
    engine.register_domain_processor(TextAnalysisDomain())
    engine.register_domain_processor(EventProcessingDomain())
    
    return engine


@pytest.fixture
def text_domain():
    """Create a text analysis domain processor"""
    return TextAnalysisDomain()


@pytest.fixture
def event_domain():
    """Create an event processing domain processor"""
    return EventProcessingDomain()
