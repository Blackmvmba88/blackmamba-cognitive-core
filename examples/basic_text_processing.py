"""
Example: Basic text processing
"""
import asyncio
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.memory.store import InMemoryStore
from blackmamba.domains.text_analysis import TextAnalysisDomain


async def main():
    """Run basic text processing example"""
    print("=== BlackMamba Cognitive Core - Text Processing Example ===\n")
    
    # Initialize components
    memory_store = InMemoryStore()
    input_processor = InputProcessor()
    engine = CognitiveEngine(
        input_processor=input_processor,
        memory_store=memory_store
    )
    
    # Register text analysis domain
    engine.register_domain_processor(TextAnalysisDomain())
    
    # Process some text
    texts = [
        "Este es un texto simple para analizar.",
        "¿Cómo funciona el sistema cognitivo de BlackMamba?",
        "La inteligencia artificial está transformando el mundo.",
    ]
    
    for i, text in enumerate(texts, 1):
        print(f"\n--- Procesando texto {i} ---")
        print(f"Input: {text}")
        
        # Create input
        input_data = await input_processor.process_text(text)
        
        # Process through engine
        response = await engine.process(input_data)
        
        # Display results
        print(f"Response ID: {response.id}")
        print(f"Domain: {response.metadata.get('domain')}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Content: {response.content.get('data', {})}")
    
    # Check memory statistics
    print("\n--- Memory Statistics ---")
    stats = await memory_store.get_stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Total accesses: {stats['total_accesses']}")
    print(f"Tags: {stats['tags']}")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    asyncio.run(main())
