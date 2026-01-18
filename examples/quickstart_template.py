#!/usr/bin/env python3
"""
BlackMamba Quickstart Template
===============================

A minimal example to get started with BlackMamba in 5 minutes.

This example shows:
1. How to initialize the cognitive engine
2. How to create a simple custom domain
3. How to process different types of input
4. How to get intelligent responses

Follow the comments to understand each step!
"""

import asyncio
from typing import Dict, Any, Optional

# Step 1: Import BlackMamba core components
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import ProcessedInput, CognitiveResponse


# Step 2: Create your custom domain
class GreetingDomain(DomainProcessor):
    """
    A simple domain that handles greetings and introductions.
    This is a minimal example to understand the domain pattern.
    """
    
    @property
    def domain_name(self) -> str:
        """Each domain needs a unique name"""
        return "greeting"
    
    async def can_handle(
        self,
        input_data: ProcessedInput,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Decide if this domain should handle the input.
        Return True if input contains greeting keywords.
        """
        if input_data.input_type != "text":
            return False
        
        # Check for greeting keywords
        greetings = ["hello", "hi", "hey", "greetings", "hola", "good morning"]
        content_lower = input_data.content.lower()
        
        return any(greeting in content_lower for greeting in greetings)
    
    async def analyze(
        self,
        input_data: ProcessedInput,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the input and extract information.
        In this case, we detect the type of greeting.
        """
        content = input_data.content.lower()
        
        greeting_type = "casual"
        if any(word in content for word in ["good morning", "good afternoon", "good evening"]):
            greeting_type = "formal"
        elif any(word in content for word in ["hey", "yo", "sup"]):
            greeting_type = "informal"
        
        return {
            "greeting_type": greeting_type,
            "original_message": input_data.content,
            "detected_language": "en" if "hello" in content else "es",
        }
    
    async def synthesize(
        self,
        input_data: ProcessedInput,
        context: Optional[Dict[str, Any]] = None,
        analysis: Optional[Dict[str, Any]] = None
    ) -> CognitiveResponse:
        """
        Generate an intelligent response based on analysis.
        """
        greeting_type = analysis.get("greeting_type", "casual") if analysis else "casual"
        
        # Choose response based on greeting type
        if greeting_type == "formal":
            response = "Good day! How may I assist you today?"
        elif greeting_type == "informal":
            response = "Hey there! What's up?"
        else:
            response = "Hello! I'm BlackMamba, your cognitive assistant. How can I help?"
        
        return CognitiveResponse(
            content=response,
            confidence=0.95,
            metadata={
                "domain": self.domain_name,
                "greeting_type": greeting_type,
                "analysis": analysis,
            }
        )


# Step 3: Create a more advanced domain (optional)
class HelpDomain(DomainProcessor):
    """A domain that provides help and guidance"""
    
    @property
    def domain_name(self) -> str:
        return "help"
    
    async def can_handle(
        self,
        input_data: ProcessedInput,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        if input_data.input_type != "text":
            return False
        
        help_keywords = ["help", "how", "what", "explain", "ayuda"]
        content_lower = input_data.content.lower()
        
        return any(keyword in content_lower for keyword in help_keywords)
    
    async def analyze(
        self,
        input_data: ProcessedInput,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        content = input_data.content.lower()
        
        topic = "general"
        if "domain" in content:
            topic = "domains"
        elif "api" in content:
            topic = "api"
        elif "example" in content:
            topic = "examples"
        
        return {
            "topic": topic,
            "question": input_data.content,
        }
    
    async def synthesize(
        self,
        input_data: ProcessedInput,
        context: Optional[Dict[str, Any]] = None,
        analysis: Optional[Dict[str, Any]] = None
    ) -> CognitiveResponse:
        topic = analysis.get("topic", "general") if analysis else "general"
        
        responses = {
            "domains": "Domains are specialized processors in BlackMamba. Create one with: blackmamba new your-domain",
            "api": "BlackMamba provides a REST API. Start the server with: python -m blackmamba.api.app",
            "examples": "Check the examples/ directory for working code samples!",
            "general": "I can help with domains, API, examples, and more. What would you like to know?",
        }
        
        return CognitiveResponse(
            content=responses[topic],
            confidence=0.85,
            metadata={
                "domain": self.domain_name,
                "topic": topic,
            }
        )


# Step 4: Main function - putting it all together
async def main():
    """
    Main function demonstrating BlackMamba usage.
    This is your template for building cognitive applications!
    """
    
    print("=" * 70)
    print("BlackMamba Quickstart Template".center(70))
    print("=" * 70)
    print()
    
    # Initialize components
    print("🚀 Initializing BlackMamba...")
    processor = InputProcessor()
    engine = CognitiveEngine(input_processor=processor)
    
    # Register your domains
    print("📦 Registering domains...")
    engine.register_domain_processor(GreetingDomain())
    engine.register_domain_processor(HelpDomain())
    print("   ✓ Greeting domain registered")
    print("   ✓ Help domain registered")
    print()
    
    # Test cases
    test_inputs = [
        "Hello! How are you?",
        "Good morning, I need assistance.",
        "Hey there!",
        "Help me understand domains",
        "What can you do?",
        "How do I use the API?",
    ]
    
    print("🧪 Testing with sample inputs:")
    print("-" * 70)
    print()
    
    for test_input in test_inputs:
        print(f"📝 Input: {test_input}")
        
        # Process the input
        input_data = await processor.process_text(test_input)
        response = await engine.process(input_data)
        
        # Display results
        print(f"🤖 Response: {response.content}")
        print(f"📊 Confidence: {response.confidence:.2%}")
        if response.metadata:
            print(f"🏷️  Domain: {response.metadata.get('domain', 'unknown')}")
        print()
    
    # Show next steps
    print("=" * 70)
    print("🎉 Quickstart Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Modify the domains above to match your use case")
    print("  2. Create a new domain: blackmamba new my-domain")
    print("  3. Start the API server: python -m blackmamba.api.app")
    print("  4. Run the interactive demo: python examples/interactive_demo.py")
    print("  5. Read the docs: docs/PLUGIN_DEVELOPMENT_GUIDE.md")
    print()
    print("Happy coding with BlackMamba! 🐍✨")
    print()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
