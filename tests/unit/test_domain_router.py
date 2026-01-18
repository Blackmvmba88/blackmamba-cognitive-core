"""
Tests for DomainRouter
"""

import pytest
from blackmamba.core.domain_router import (
    DomainRouter,
    DefaultRoutingStrategy,
    RoutingScore,
)
from blackmamba.core.domain_registry import DomainRegistry, DomainHealth
from blackmamba.core.types import Input, ProcessingContext, InputType
from tests.unit.test_domain_registry import MockDomainProcessor


@pytest.fixture
def registry():
    """Create a fresh domain registry"""
    return DomainRegistry()


@pytest.fixture
def router(registry):
    """Create a domain router"""
    return DomainRouter(registry)


@pytest.fixture
def sample_input():
    """Create a sample input"""
    return Input(
        id="test-input",
        type=InputType.TEXT,
        content={"text": "Hello world"},
        metadata={}
    )


@pytest.fixture
def sample_context():
    """Create a sample context"""
    return ProcessingContext(input_id="test-input")


@pytest.mark.asyncio
async def test_route_basic(registry, router, sample_input, sample_context):
    """Test basic routing"""
    proc = MockDomainProcessor("test_domain", can_handle_result=True)
    registry.register(proc, priority=5)
    
    result = await router.route(sample_input, sample_context)
    
    assert result is not None
    domain_name, processor, score = result
    assert domain_name == "test_domain"
    assert processor == proc
    assert score.can_handle is True
    assert score.score > 0


@pytest.mark.asyncio
async def test_route_no_domains(router, sample_input, sample_context):
    """Test routing with no registered domains"""
    result = await router.route(sample_input, sample_context)
    assert result is None


@pytest.mark.asyncio
async def test_route_no_matching_domain(registry, router, sample_input, sample_context):
    """Test routing when no domain can handle input"""
    proc = MockDomainProcessor("test_domain", can_handle_result=False)
    registry.register(proc)
    
    result = await router.route(sample_input, sample_context)
    assert result is None


@pytest.mark.asyncio
async def test_route_priority(registry, router, sample_input, sample_context):
    """Test that higher priority domains are preferred"""
    proc_low = MockDomainProcessor("low_priority", can_handle_result=True)
    proc_high = MockDomainProcessor("high_priority", can_handle_result=True)
    
    registry.register(proc_low, priority=1)
    registry.register(proc_high, priority=10)
    
    result = await router.route(sample_input, sample_context)
    
    assert result is not None
    domain_name, processor, score = result
    assert domain_name == "high_priority"


@pytest.mark.asyncio
async def test_route_all(registry, router, sample_input, sample_context):
    """Test getting all matching domains"""
    proc1 = MockDomainProcessor("domain1", can_handle_result=True)
    proc2 = MockDomainProcessor("domain2", can_handle_result=True)
    proc3 = MockDomainProcessor("domain3", can_handle_result=False)
    
    registry.register(proc1, priority=5)
    registry.register(proc2, priority=8)
    registry.register(proc3, priority=10)
    
    results = await router.route_all(sample_input, sample_context)
    
    assert len(results) == 2
    # Should be sorted by score (priority matters)
    assert results[0][0] == "domain2"  # Higher priority
    assert results[1][0] == "domain1"


@pytest.mark.asyncio
async def test_route_exclude(registry, router, sample_input, sample_context):
    """Test routing with exclusions"""
    proc1 = MockDomainProcessor("domain1", can_handle_result=True)
    proc2 = MockDomainProcessor("domain2", can_handle_result=True)
    
    registry.register(proc1, priority=10)
    registry.register(proc2, priority=5)
    
    # Without exclusion, should get domain1
    result = await router.route(sample_input, sample_context)
    assert result[0] == "domain1"
    
    # With exclusion, should get domain2
    result = await router.route(sample_input, sample_context, exclude=["domain1"])
    assert result[0] == "domain2"


def test_fallback_chain(router):
    """Test setting and getting fallback chains"""
    router.set_fallback_chain("primary", ["fallback1", "fallback2"])
    
    chain = router.get_fallback_chain("primary")
    assert chain == ["fallback1", "fallback2"]


def test_circuit_breaker(router):
    """Test circuit breaker functionality"""
    domain_name = "test_domain"
    
    # Record failures
    for i in range(5):
        router.record_failure(domain_name)
    
    # Circuit should be broken
    assert router._is_circuit_broken(domain_name)
    
    # Reset
    router.reset_circuit_breaker(domain_name)
    assert not router._is_circuit_broken(domain_name)


def test_circuit_breaker_success_resets(router):
    """Test that success resets circuit breaker"""
    domain_name = "test_domain"
    
    # Record some failures
    router.record_failure(domain_name)
    router.record_failure(domain_name)
    
    # Record success
    router.record_success(domain_name)
    
    # Failures should be reset
    assert not router._is_circuit_broken(domain_name)


@pytest.mark.asyncio
async def test_route_skips_circuit_broken(registry, router, sample_input, sample_context):
    """Test that routing skips circuit-broken domains"""
    proc1 = MockDomainProcessor("domain1", can_handle_result=True)
    proc2 = MockDomainProcessor("domain2", can_handle_result=True)
    
    registry.register(proc1, priority=10)
    registry.register(proc2, priority=5)
    
    # Break circuit for domain1
    for i in range(5):
        router.record_failure("domain1")
    
    # Should route to domain2 instead
    result = await router.route(sample_input, sample_context)
    assert result is not None
    assert result[0] == "domain2"


@pytest.mark.asyncio
async def test_routing_strategy_scoring():
    """Test default routing strategy scoring"""
    strategy = DefaultRoutingStrategy()
    
    proc = MockDomainProcessor("test", can_handle_result=True)
    input_data = Input(
        id="test",
        type=InputType.TEXT,
        content={"text": "test"},
        metadata={}
    )
    context = ProcessingContext(input_id="test")
    
    # Test with different parameters
    score = await strategy.score(
        domain_name="test",
        processor=proc,
        input_data=input_data,
        context=context,
        priority=10,
        health=DomainHealth.HEALTHY,
    )
    
    assert score.can_handle is True
    assert score.score > 0.5  # Base + priority bonus
    assert score.priority == 10
    assert score.health == DomainHealth.HEALTHY


@pytest.mark.asyncio
async def test_routing_strategy_health_penalty():
    """Test that unhealthy domains get penalized"""
    strategy = DefaultRoutingStrategy()
    
    proc = MockDomainProcessor("test", can_handle_result=True)
    input_data = Input(
        id="test",
        type=InputType.TEXT,
        content={"text": "test"},
        metadata={}
    )
    context = ProcessingContext(input_id="test")
    
    # Healthy domain
    healthy_score = await strategy.score(
        domain_name="test",
        processor=proc,
        input_data=input_data,
        context=context,
        priority=5,
        health=DomainHealth.HEALTHY,
    )
    
    # Unhealthy domain
    unhealthy_score = await strategy.score(
        domain_name="test",
        processor=proc,
        input_data=input_data,
        context=context,
        priority=5,
        health=DomainHealth.UNHEALTHY,
    )
    
    # Unhealthy should have lower score
    assert unhealthy_score.score < healthy_score.score


def test_get_stats(router):
    """Test getting router statistics"""
    router.set_fallback_chain("primary", ["fallback"])
    router.record_failure("test")
    
    stats = router.get_stats()
    
    assert "fallback_chains" in stats
    assert "circuit_breaker_failures" in stats
    assert "circuit_breaker_threshold" in stats
    assert "primary" in stats["fallback_chains"]
    assert "test" in stats["circuit_breaker_failures"]
