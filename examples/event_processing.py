"""
Example: Event processing and monitoring
"""
import asyncio
from datetime import datetime
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.memory.store import InMemoryStore
from blackmamba.domains.event_processing import EventProcessingDomain


async def main():
    """Run event processing example"""
    print("=== BlackMamba Cognitive Core - Event Processing Example ===\n")
    
    # Initialize components
    memory_store = InMemoryStore()
    input_processor = InputProcessor()
    engine = CognitiveEngine(
        input_processor=input_processor,
        memory_store=memory_store
    )
    
    # Register event processing domain
    engine.register_domain_processor(EventProcessingDomain())
    
    # Simulate various events
    events = [
        ("user_login", {"user_id": "user123", "ip": "192.168.1.1"}),
        ("error_occurred", {"error_code": "500", "service": "api"}),
        ("data_update", {"records": 150, "table": "users"}),
        ("user_login", {"user_id": "user456", "ip": "192.168.1.2"}),
        ("critical_alert", {"severity": "high", "message": "System overload"}),
        ("user_login", {"user_id": "user789", "ip": "192.168.1.3"}),
    ]
    
    for i, (event_type, event_data) in enumerate(events, 1):
        print(f"\n--- Processing Event {i} ---")
        print(f"Type: {event_type}")
        print(f"Data: {event_data}")
        
        # Create input
        input_data = await input_processor.process_event(
            event_type=event_type,
            event_data=event_data
        )
        
        # Process through engine
        response = await engine.process(input_data)
        
        # Display results
        print(f"Response ID: {response.id}")
        print(f"Domain: {response.metadata.get('domain')}")
        print(f"Confidence: {response.confidence:.2f}")
        
        response_data = response.content.get('data', {})
        print(f"Priority: {response_data.get('priority')}")
        
        if response_data.get('actions'):
            print(f"Actions: {response_data['actions']}")
        
        if response_data.get('recommendations'):
            print(f"Recommendations: {response_data['recommendations']}")
    
    # Search for specific events in memory
    print("\n--- Searching Memory for Login Events ---")
    results = await memory_store.search({"content_contains": "user_login"})
    print(f"Found {len(results)} login events")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    asyncio.run(main())
