"""
Example: Using the new Domain Registry and Router

This example demonstrates the new registry-based architecture
with hot-plug capabilities, intelligent routing, and health monitoring.
"""

import asyncio
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.domains.text_analysis import TextAnalysisDomain
from blackmamba.domains.event_processing import EventProcessingDomain
from blackmamba.domains.electronics_repair import ElectronicsRepairDomain


async def main():
    print("=" * 60)
    print("BlackMamba Cognitive Core - Registry & Router Example")
    print("=" * 60)
    print()
    
    # Initialize engine with registry mode
    print("1. Initializing engine with registry mode...")
    processor = InputProcessor()
    engine = CognitiveEngine(
        input_processor=processor,
        use_registry=True  # Enable new registry-based architecture
    )
    print("✓ Engine initialized with DomainRegistry and Router\n")
    
    # Register domains with priorities
    print("2. Registering domains with priorities...")
    
    # High priority domain for technical queries
    engine.register_domain_processor(
        ElectronicsRepairDomain(),
        priority=10,
        version="1.0.0"
    )
    print("  ✓ ElectronicsRepairDomain (priority=10)")
    
    # Medium priority for events
    engine.register_domain_processor(
        EventProcessingDomain(),
        priority=5,
        version="1.0.0"
    )
    print("  ✓ EventProcessingDomain (priority=5)")
    
    # Lower priority for general text
    engine.register_domain_processor(
        TextAnalysisDomain(),
        priority=1,
        version="1.0.0"
    )
    print("  ✓ TextAnalysisDomain (priority=1)\n")
    
    # Get domain statistics
    print("3. Domain Registry Statistics:")
    stats = engine.get_domain_stats()
    print(f"  Mode: {stats['mode']}")
    print(f"  Total domains: {stats['registry']['total_domains']}")
    print(f"  Enabled domains: {stats['registry']['enabled_domains']}")
    print()
    
    # Perform health check
    print("4. Performing health check on all domains...")
    health_status = await engine.health_check_domains()
    for domain, status in health_status.items():
        status_emoji = "✅" if status.value == "healthy" else "❌"
        print(f"  {status_emoji} {domain}: {status.value}")
    print()
    
    # Process a text input
    print("5. Processing text input (should route to TextAnalysisDomain)...")
    text_input = await processor.process_text(
        "La inteligencia artificial está transformando la industria"
    )
    response = await engine.process(text_input)
    print(f"  Domain selected: {response.metadata.get('domain', 'N/A')}")
    print(f"  Confidence: {response.confidence:.2f}")
    print()
    
    # Process an event input
    print("6. Processing event input (should route to EventProcessingDomain)...")
    event_input = await processor.process_event(
        event_type="system_alert",
        event_data={"severity": "high", "message": "CPU usage at 95%"}
    )
    response = await engine.process(event_input)
    print(f"  Domain selected: {response.metadata.get('domain', 'N/A')}")
    print(f"  Confidence: {response.confidence:.2f}")
    print()
    
    # Demonstrate hot-plug: disable a domain
    print("7. Demonstrating hot-plug: disabling TextAnalysisDomain...")
    engine.registry.disable("text_analysis")
    print("  ✓ Domain disabled\n")
    
    # Try processing text again (should fail to route or use fallback)
    print("8. Attempting to process text with TextAnalysisDomain disabled...")
    try:
        text_input2 = await processor.process_text(
            "Este texto debería fallar o usar otro dominio"
        )
        response = await engine.process(text_input2)
        print(f"  Fallback domain used: {response.metadata.get('domain', 'default')}")
    except Exception as e:
        print(f"  Expected: No domain could handle the input")
    print()
    
    # Re-enable the domain
    print("9. Re-enabling TextAnalysisDomain...")
    engine.registry.enable("text_analysis")
    print("  ✓ Domain re-enabled\n")
    
    # Test circuit breaker by simulating failures
    print("10. Testing circuit breaker (simulating failures)...")
    for i in range(5):
        engine.router.record_failure("text_analysis")
    
    router_stats = engine.router.get_stats()
    broken_domains = router_stats.get("circuit_broken_domains", [])
    if "text_analysis" in broken_domains:
        print("  ✓ Circuit breaker activated for text_analysis")
        print(f"  Failures: {router_stats['circuit_breaker_failures'].get('text_analysis', 0)}")
    print()
    
    # Reset circuit breaker
    print("11. Resetting circuit breaker...")
    engine.router.reset_circuit_breaker("text_analysis")
    print("  ✓ Circuit breaker reset\n")
    
    # Show final statistics
    print("12. Final Registry Statistics:")
    final_stats = engine.get_domain_stats()
    print(f"  Registered domains: {list(final_stats['registry']['domains'].keys())}")
    print(f"  Health status:")
    for domain, info in final_stats['registry']['domains'].items():
        print(f"    - {domain}: {info['health']} (priority={info['priority']})")
    print()
    
    # Demonstrate fallback chains
    print("13. Setting up fallback chain...")
    engine.router.set_fallback_chain(
        "electronics_repair",
        ["text_analysis", "event_processing"]
    )
    fallback = engine.router.get_fallback_chain("electronics_repair")
    print(f"  ✓ Fallback chain for electronics_repair: {fallback}\n")
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print()
    print("Key features demonstrated:")
    print("  ✓ Domain registration with priorities")
    print("  ✓ Intelligent routing based on scoring")
    print("  ✓ Health monitoring")
    print("  ✓ Hot-plug (enable/disable domains at runtime)")
    print("  ✓ Circuit breaker for failure protection")
    print("  ✓ Fallback chains")
    print("  ✓ Statistics and observability")


if __name__ == "__main__":
    asyncio.run(main())
