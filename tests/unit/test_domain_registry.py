"""
Tests for DomainRegistry
"""

import pytest
from datetime import datetime
from blackmamba.core.domain_registry import (
    DomainRegistry,
    DomainHealth,
    DomainInfo,
)
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import Input, ProcessingContext, Response


class MockDomainProcessor(DomainProcessor):
    """Mock domain processor for testing"""
    
    def __init__(self, name: str, can_handle_result: bool = True):
        self.name = name
        self.can_handle_result = can_handle_result
        self.health_check_result = True
    
    @property
    def domain_name(self) -> str:
        return self.name
    
    async def can_handle(self, input_data: Input, context: ProcessingContext) -> bool:
        return self.can_handle_result
    
    async def analyze(self, input_data: Input, context: ProcessingContext):
        return {"analyzed": True}
    
    async def synthesize(self, input_data: Input, context: ProcessingContext, analysis_results):
        return Response(
            id="test",
            input_id=input_data.id,
            content={"message": "test"},
            confidence=0.8,
            metadata={}
        )
    
    async def health_check(self) -> bool:
        return self.health_check_result


@pytest.fixture
def registry():
    """Create a fresh domain registry for each test"""
    return DomainRegistry()


@pytest.fixture
def mock_processor():
    """Create a mock domain processor"""
    return MockDomainProcessor("test_domain")


def test_registry_initialization(registry):
    """Test registry initializes correctly"""
    assert len(registry.list_domains()) == 0
    stats = registry.get_stats()
    assert stats["total_domains"] == 0


def test_register_domain(registry, mock_processor):
    """Test registering a domain"""
    result = registry.register(mock_processor, version="1.0.0", priority=5)
    
    assert result is True
    assert "test_domain" in registry.list_domains()
    
    info = registry.get_info("test_domain")
    assert info is not None
    assert info.processor == mock_processor
    assert info.version == "1.0.0"
    assert info.priority == 5
    assert info.enabled is True


def test_register_duplicate_domain(registry, mock_processor):
    """Test registering a domain twice fails"""
    registry.register(mock_processor)
    result = registry.register(mock_processor)
    
    assert result is False
    assert len(registry.list_domains()) == 1


def test_unregister_domain(registry, mock_processor):
    """Test unregistering a domain"""
    registry.register(mock_processor)
    result = registry.unregister("test_domain")
    
    assert result is True
    assert "test_domain" not in registry.list_domains()


def test_unregister_nonexistent_domain(registry):
    """Test unregistering a non-existent domain"""
    result = registry.unregister("nonexistent")
    assert result is False


def test_get_domain(registry, mock_processor):
    """Test getting a domain processor"""
    registry.register(mock_processor)
    processor = registry.get("test_domain")
    
    assert processor == mock_processor


def test_get_nonexistent_domain(registry):
    """Test getting a non-existent domain"""
    processor = registry.get("nonexistent")
    assert processor is None


def test_list_domains(registry):
    """Test listing domains"""
    proc1 = MockDomainProcessor("domain1")
    proc2 = MockDomainProcessor("domain2")
    
    registry.register(proc1)
    registry.register(proc2)
    
    domains = registry.list_domains()
    assert len(domains) == 2
    assert "domain1" in domains
    assert "domain2" in domains


def test_list_by_priority(registry):
    """Test listing domains by priority"""
    proc1 = MockDomainProcessor("low_priority")
    proc2 = MockDomainProcessor("high_priority")
    proc3 = MockDomainProcessor("medium_priority")
    
    registry.register(proc1, priority=1)
    registry.register(proc2, priority=10)
    registry.register(proc3, priority=5)
    
    domains = registry.list_by_priority()
    assert domains == ["high_priority", "medium_priority", "low_priority"]


def test_enable_disable_domain(registry, mock_processor):
    """Test enabling and disabling a domain"""
    registry.register(mock_processor)
    
    # Disable
    result = registry.disable("test_domain")
    assert result is True
    
    processor = registry.get("test_domain")
    assert processor is None  # Disabled domains return None
    
    enabled_domains = registry.list_domains(enabled_only=True)
    assert "test_domain" not in enabled_domains
    
    # Re-enable
    result = registry.enable("test_domain")
    assert result is True
    
    processor = registry.get("test_domain")
    assert processor == mock_processor


@pytest.mark.asyncio
async def test_health_check(registry, mock_processor):
    """Test health check"""
    registry.register(mock_processor)
    
    health = await registry.health_check("test_domain")
    assert health == DomainHealth.HEALTHY
    
    info = registry.get_info("test_domain")
    assert info.health == DomainHealth.HEALTHY
    assert info.last_health_check is not None


@pytest.mark.asyncio
async def test_health_check_unhealthy(registry):
    """Test health check for unhealthy domain"""
    proc = MockDomainProcessor("unhealthy")
    proc.health_check_result = False
    
    registry.register(proc)
    
    health = await registry.health_check("unhealthy")
    assert health == DomainHealth.UNHEALTHY


@pytest.mark.asyncio
async def test_health_check_all(registry):
    """Test health check for all domains"""
    proc1 = MockDomainProcessor("domain1")
    proc2 = MockDomainProcessor("domain2")
    
    registry.register(proc1)
    registry.register(proc2)
    
    results = await registry.health_check_all()
    
    assert len(results) == 2
    assert results["domain1"] == DomainHealth.HEALTHY
    assert results["domain2"] == DomainHealth.HEALTHY


def test_dependencies(registry):
    """Test domain dependencies"""
    proc1 = MockDomainProcessor("base")
    proc2 = MockDomainProcessor("dependent")
    
    # Register base domain
    registry.register(proc1)
    
    # Register dependent domain
    registry.register(proc2, dependencies=["base"])
    
    info = registry.get_info("dependent")
    assert "base" in info.dependencies


def test_dependencies_missing(registry):
    """Test registering with missing dependencies fails"""
    proc = MockDomainProcessor("dependent")
    
    with pytest.raises(ValueError, match="Missing dependencies"):
        registry.register(proc, dependencies=["nonexistent"])


def test_unregister_with_dependents(registry):
    """Test unregistering a domain with dependents fails"""
    proc1 = MockDomainProcessor("base")
    proc2 = MockDomainProcessor("dependent")
    
    registry.register(proc1)
    registry.register(proc2, dependencies=["base"])
    
    with pytest.raises(ValueError, match="has dependents"):
        registry.unregister("base")


def test_event_handlers(registry, mock_processor):
    """Test event handlers"""
    events = []
    
    def handler(domain_name, info):
        events.append(("register", domain_name))
    
    registry.on_event("register", handler)
    registry.register(mock_processor)
    
    assert len(events) == 1
    assert events[0] == ("register", "test_domain")


def test_get_stats(registry):
    """Test getting registry statistics"""
    proc1 = MockDomainProcessor("domain1")
    proc2 = MockDomainProcessor("domain2")
    
    registry.register(proc1, version="1.0.0", priority=5)
    registry.register(proc2, version="2.0.0", priority=3)
    registry.disable("domain2")
    
    stats = registry.get_stats()
    
    assert stats["total_domains"] == 2
    assert stats["enabled_domains"] == 1
    assert "domain1" in stats["domains"]
    assert "domain2" in stats["domains"]
    assert stats["domains"]["domain1"]["version"] == "1.0.0"
    assert stats["domains"]["domain1"]["priority"] == 5
    assert stats["domains"]["domain2"]["enabled"] is False
