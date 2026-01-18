# 🧩 Plugin Development Guide

## Building Cognitive Plugins for BlackMamba

Welcome to the BlackMamba Plugin Development Guide! This document will help you create cognitive domains that work as pluggable microservices in the BlackMamba ecosystem.

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Creating Your First Plugin](#creating-your-first-plugin)
- [Plugin Interface](#plugin-interface)
- [Best Practices](#best-practices)
- [Advanced Features](#advanced-features)
- [Testing](#testing)
- [Deployment](#deployment)
- [Examples](#examples)

---

## Introduction

### What is a Cognitive Plugin?

A cognitive plugin (or domain) in BlackMamba is a specialized module that:

- **Handles specific types of input** (e.g., electronic measurements, logistics data, medical readings)
- **Analyzes data** using domain-specific knowledge
- **Generates intelligent responses** with recommendations
- **Learns from outcomes** to improve over time
- **Integrates seamlessly** with the cognitive engine

### Why Create Plugins?

Plugins allow you to:

✅ **Specialize**: Focus on a specific vertical or use case  
✅ **Reuse**: Leverage BlackMamba's cognitive infrastructure  
✅ **Distribute**: Share domains with the community  
✅ **Scale**: Deploy domains independently  
✅ **Evolve**: Update domains without changing the core engine

### Plugin Philosophy

BlackMamba follows these principles:

1. **One domain, one expertise**: Each plugin is an expert in one area
2. **Composable**: Plugins work together through the cognitive engine
3. **Observable**: Clear confidence scores and metadata
4. **Learnable**: Can improve from feedback
5. **Deployable**: Work locally, in cloud, or at edge

---

## Quick Start

### Option 1: Use the CLI (Recommended)

```bash
# Create a new domain
blackmamba new logistics "Handles supply chain optimization"

# This creates:
# - blackmamba/domains/logistics.py (domain implementation)
# - examples/logistics_example.py (usage example)
# - tests/unit/test_logistics.py (test suite)
# - README for the domain
```

### Option 2: Start from Template

```bash
# Copy the quickstart template
cp examples/quickstart_template.py my_domain.py

# Edit and customize
vim my_domain.py
```

### Option 3: Clone an Example

```bash
# Use an existing domain as a template
cp blackmamba/domains/text_analysis.py blackmamba/domains/my_domain.py

# Customize it
```

---

## Architecture Overview

### The Cognitive Cycle

Every plugin participates in this cycle:

```
┌─────────────┐
│   INPUT     │ ← Text, Events, Measurements, Images
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  can_handle()                           │
│  "Should I process this?"               │
└──────┬──────────────────────────────────┘
       │ YES
       ↓
┌─────────────────────────────────────────┐
│  analyze()                              │
│  "Extract insights and patterns"        │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  synthesize()                           │
│  "Generate intelligent response"        │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────┐
│   OUTPUT    │ → Response + Confidence + Metadata
└─────────────┘
```

### Plugin Interface

Every plugin implements the `DomainProcessor` interface:

```python
class DomainProcessor:
    @property
    def domain_name(self) -> str:
        """Unique identifier for the domain"""
        pass
    
    async def can_handle(self, input_data, context) -> bool:
        """Decide if this domain should process the input"""
        pass
    
    async def analyze(self, input_data, context) -> Dict:
        """Extract insights from the input"""
        pass
    
    async def synthesize(self, input_data, context, analysis) -> CognitiveResponse:
        """Generate an intelligent response"""
        pass
```

---

## Creating Your First Plugin

### Step 1: Define Your Domain

Ask yourself:

- **What problem does it solve?** (e.g., "Diagnose electronic board failures")
- **What input does it need?** (e.g., "Voltage measurements and symptoms")
- **What output does it produce?** (e.g., "Fault diagnosis and repair recommendations")
- **What knowledge does it use?** (e.g., "Electronics ontology, historical cases")

### Step 2: Create the Plugin Structure

```python
"""
My Custom Domain
"""

from typing import Dict, Any, Optional
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.types import ProcessedInput, CognitiveResponse


class MyCustomDomain(DomainProcessor):
    """
    Domain for [your use case]
    
    Handles: [what it handles]
    Provides: [what it provides]
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize with optional configuration"""
        super().__init__()
        self.config = config or {}
        # Load knowledge base, models, etc.
        self.knowledge_base = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """Load domain-specific knowledge"""
        return {
            # Your knowledge here
        }
    
    @property
    def domain_name(self) -> str:
        return "my_custom_domain"
    
    # Implement the three core methods...
```

### Step 3: Implement can_handle()

This method determines if your domain should process the input.

```python
async def can_handle(
    self,
    input_data: ProcessedInput,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Return True if this domain should handle the input.
    """
    # Example 1: Check input type
    if input_data.input_type == "event":
        event_type = input_data.metadata.get("event_type")
        return event_type in ["measurement", "sensor_reading"]
    
    # Example 2: Check for keywords
    if input_data.input_type == "text":
        keywords = ["diagnose", "repair", "fault"]
        return any(kw in input_data.content.lower() for kw in keywords)
    
    # Example 3: Check metadata
    if "board_type" in input_data.metadata:
        return True
    
    return False
```

**Tips:**
- Be specific but not too narrow
- Consider multiple input types
- Return quickly (this is called often)
- Use confidence thresholds if needed

### Step 4: Implement analyze()

Extract insights and structure the data.

```python
async def analyze(
    self,
    input_data: ProcessedInput,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze the input and extract insights.
    """
    analysis = {
        "domain": self.domain_name,
        "timestamp": input_data.timestamp,
    }
    
    # Example: Extract features
    if input_data.input_type == "event":
        # Extract event data
        analysis["event_type"] = input_data.metadata.get("event_type")
        analysis["features"] = self._extract_features(input_data)
    
    # Example: Pattern matching
    patterns = self._match_patterns(input_data)
    analysis["matched_patterns"] = patterns
    
    # Example: Calculate scores
    analysis["severity_score"] = self._calculate_severity(input_data)
    
    # Example: Look up knowledge base
    analysis["knowledge_match"] = self._lookup_knowledge(input_data)
    
    return analysis
```

**Tips:**
- Structure your analysis for easy synthesis
- Include confidence/scores where relevant
- Reference external knowledge
- Keep it deterministic when possible

### Step 5: Implement synthesize()

Generate the intelligent response.

```python
async def synthesize(
    self,
    input_data: ProcessedInput,
    context: Optional[Dict[str, Any]] = None,
    analysis: Optional[Dict[str, Any]] = None
) -> CognitiveResponse:
    """
    Generate response based on analysis.
    """
    # Calculate confidence
    confidence = self._calculate_confidence(analysis)
    
    # Generate main response
    content = self._generate_response_text(analysis)
    
    # Generate recommendations
    recommendations = self._generate_recommendations(analysis)
    
    # Compile metadata
    metadata = {
        "domain": self.domain_name,
        "analysis": analysis,
        "recommendations": recommendations,
        "confidence_breakdown": {
            "data_quality": 0.95,
            "pattern_match": 0.80,
            "knowledge_coverage": 0.85,
        }
    }
    
    return CognitiveResponse(
        content=content,
        confidence=confidence,
        metadata=metadata
    )
```

**Tips:**
- Always include confidence score (0.0-1.0)
- Provide actionable recommendations
- Include metadata for observability
- Explain your reasoning when possible

---

## Plugin Interface

### Required Methods

#### 1. domain_name

```python
@property
def domain_name(self) -> str:
    """Unique identifier for this domain"""
    return "my_domain"
```

- Must be unique across all domains
- Use snake_case
- Keep it descriptive but short

#### 2. can_handle()

```python
async def can_handle(
    self,
    input_data: ProcessedInput,
    context: Optional[Dict[str, Any]] = None
) -> bool:
```

**Parameters:**
- `input_data`: The processed input (text, event, audio, etc.)
- `context`: Optional context from previous processing

**Returns:**
- `bool`: True if domain should handle this input

**Performance:**
- Must be fast (<10ms typically)
- Called for every input
- Can return True for multiple domains

#### 3. analyze()

```python
async def analyze(
    self,
    input_data: ProcessedInput,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

**Parameters:**
- `input_data`: The processed input
- `context`: Optional context

**Returns:**
- `Dict`: Analysis results (structure is up to you)

**Best Practices:**
- Structure for easy synthesis
- Include intermediate calculations
- Add metadata for debugging

#### 4. synthesize()

```python
async def synthesize(
    self,
    input_data: ProcessedInput,
    context: Optional[Dict[str, Any]] = None,
    analysis: Optional[Dict[str, Any]] = None
) -> CognitiveResponse:
```

**Parameters:**
- `input_data`: The processed input
- `context`: Optional context
- `analysis`: Results from analyze()

**Returns:**
- `CognitiveResponse`: The final response

---

## Best Practices

### 1. Design Principles

✅ **Single Responsibility**: One domain, one expertise  
✅ **Fail Gracefully**: Return low confidence instead of errors  
✅ **Be Observable**: Include metadata for debugging  
✅ **Be Composable**: Work well with other domains  
✅ **Be Testable**: Write unit tests for each method

### 2. Confidence Scoring

```python
def _calculate_confidence(self, analysis: Dict) -> float:
    """
    Calculate overall confidence score.
    
    Consider:
    - Data quality (completeness, validity)
    - Pattern match strength
    - Knowledge base coverage
    - Historical success rate
    """
    scores = [
        analysis.get("data_quality", 0.5),
        analysis.get("pattern_strength", 0.5),
        analysis.get("knowledge_match", 0.5),
    ]
    
    # Weighted average
    return sum(scores) / len(scores)
```

### 3. Error Handling

```python
async def analyze(self, input_data, context=None):
    try:
        # Your analysis logic
        result = self._complex_analysis(input_data)
        return result
    
    except Exception as e:
        # Log the error
        logger.error(f"Analysis failed: {e}")
        
        # Return minimal valid analysis
        return {
            "domain": self.domain_name,
            "error": str(e),
            "confidence": 0.0,
        }
```

### 4. Memory Integration

```python
from blackmamba.memory.store import InMemoryStore

class MyDomain(DomainProcessor):
    def __init__(self, memory_store=None):
        self.memory = memory_store or InMemoryStore()
    
    async def analyze(self, input_data, context=None):
        # Look up similar cases
        similar = await self.memory.search(
            tags=[self.domain_name],
            limit=5
        )
        
        return {
            "similar_cases": similar,
            # ... other analysis
        }
    
    async def synthesize(self, input_data, context=None, analysis=None):
        # Store this case for future reference
        await self.memory.store(
            content=input_data.content,
            tags=[self.domain_name, "processed"],
            metadata=analysis
        )
        
        # Generate response...
```

### 5. Configuration

```python
class MyDomain(DomainProcessor):
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Load settings with defaults
        self.threshold = self.config.get("threshold", 0.7)
        self.max_results = self.config.get("max_results", 10)
        self.enable_learning = self.config.get("enable_learning", True)

# Usage
domain = MyDomain(config={
    "threshold": 0.8,
    "max_results": 5,
})
```

---

## Advanced Features

### 1. Multi-Step Processing

```python
async def analyze(self, input_data, context=None):
    # Step 1: Preprocessing
    preprocessed = await self._preprocess(input_data)
    
    # Step 2: Feature extraction
    features = await self._extract_features(preprocessed)
    
    # Step 3: Pattern matching
    patterns = await self._match_patterns(features)
    
    # Step 4: Reasoning
    reasoning = await self._reason(patterns)
    
    return {
        "features": features,
        "patterns": patterns,
        "reasoning": reasoning,
    }
```

### 2. External API Integration

```python
import aiohttp

class MyDomain(DomainProcessor):
    async def analyze(self, input_data, context=None):
        # Call external API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com/data") as resp:
                external_data = await resp.json()
        
        # Combine with local analysis
        return {
            "local_analysis": self._local_analysis(input_data),
            "external_data": external_data,
        }
```

### 3. Caching

```python
from functools import lru_cache

class MyDomain(DomainProcessor):
    @lru_cache(maxsize=128)
    def _expensive_lookup(self, key: str):
        """Cache expensive computations"""
        # Expensive operation
        return result
```

### 4. Batching

```python
async def analyze_batch(
    self,
    inputs: List[ProcessedInput],
    context: Optional[Dict] = None
) -> List[Dict]:
    """Process multiple inputs efficiently"""
    # Batch API call or vectorized operation
    results = await self._batch_process(inputs)
    return results
```

---

## Testing

### Unit Tests Template

```python
import pytest
from blackmamba.core.input_processor import InputProcessor
from blackmamba.domains.my_domain import MyDomain


@pytest.fixture
def domain():
    """Create domain instance"""
    return MyDomain()


@pytest.fixture
def processor():
    """Create input processor"""
    return InputProcessor()


@pytest.mark.asyncio
async def test_domain_name(domain):
    """Test domain name is correct"""
    assert domain.domain_name == "my_domain"


@pytest.mark.asyncio
async def test_can_handle(domain, processor):
    """Test input detection"""
    # Positive case
    input_data = await processor.process_text("relevant keyword")
    assert await domain.can_handle(input_data) == True
    
    # Negative case
    input_data = await processor.process_text("irrelevant text")
    assert await domain.can_handle(input_data) == False


@pytest.mark.asyncio
async def test_analyze(domain, processor):
    """Test analysis"""
    input_data = await processor.process_text("test input")
    analysis = await domain.analyze(input_data)
    
    assert isinstance(analysis, dict)
    assert "domain" in analysis
    assert analysis["domain"] == "my_domain"


@pytest.mark.asyncio
async def test_synthesize(domain, processor):
    """Test synthesis"""
    input_data = await processor.process_text("test input")
    analysis = await domain.analyze(input_data)
    response = await domain.synthesize(input_data, analysis=analysis)
    
    assert response.content is not None
    assert 0 <= response.confidence <= 1
    assert response.metadata is not None


@pytest.mark.asyncio
async def test_end_to_end(domain, processor):
    """Test complete pipeline"""
    input_data = await processor.process_text("test input")
    
    if await domain.can_handle(input_data):
        analysis = await domain.analyze(input_data)
        response = await domain.synthesize(input_data, analysis=analysis)
        
        assert response is not None
        assert response.confidence > 0
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_with_engine():
    """Test domain with cognitive engine"""
    from blackmamba.core.engine import CognitiveEngine
    
    processor = InputProcessor()
    engine = CognitiveEngine(input_processor=processor)
    
    # Register domain
    engine.register_domain_processor(MyDomain())
    
    # Process input
    input_data = await processor.process_text("test")
    response = await engine.process(input_data)
    
    assert response is not None
```

---

## Deployment

### As Part of Core Engine

```python
# In your application
from blackmamba.core.engine import CognitiveEngine
from blackmamba.domains.my_domain import MyDomain

engine = CognitiveEngine()
engine.register_domain_processor(MyDomain())
```

### As Standalone Service

```python
# my_domain_service.py
from fastapi import FastAPI
from blackmamba.domains.my_domain import MyDomain
from blackmamba.core.input_processor import InputProcessor

app = FastAPI()
domain = MyDomain()
processor = InputProcessor()

@app.post("/process")
async def process(text: str):
    input_data = await processor.process_text(text)
    
    if await domain.can_handle(input_data):
        analysis = await domain.analyze(input_data)
        response = await domain.synthesize(input_data, analysis=analysis)
        return response.dict()
    
    return {"error": "Cannot handle input"}
```

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY blackmamba/domains/my_domain.py ./blackmamba/domains/

CMD ["python", "-m", "my_domain_service"]
```

---

## Examples

### Example 1: Simple Keyword Domain

```python
class KeywordDomain(DomainProcessor):
    """Detects and responds to specific keywords"""
    
    @property
    def domain_name(self) -> str:
        return "keyword"
    
    async def can_handle(self, input_data, context=None):
        keywords = ["urgent", "emergency", "critical"]
        return any(kw in input_data.content.lower() for kw in keywords)
    
    async def analyze(self, input_data, context=None):
        content = input_data.content.lower()
        return {
            "urgency": "high" if "emergency" in content else "medium",
            "keywords_found": [kw for kw in ["urgent", "emergency"] if kw in content]
        }
    
    async def synthesize(self, input_data, context=None, analysis=None):
        urgency = analysis.get("urgency", "medium")
        
        if urgency == "high":
            message = "⚠️ EMERGENCY detected. Escalating immediately."
        else:
            message = "Noted as urgent. Processing with priority."
        
        return CognitiveResponse(
            content=message,
            confidence=0.9,
            metadata={"urgency": urgency}
        )
```

### Example 2: Pattern Matching Domain

```python
import re

class PatternDomain(DomainProcessor):
    """Matches regex patterns"""
    
    def __init__(self):
        self.patterns = {
            "email": r'[\w\.-]+@[\w\.-]+\.\w+',
            "phone": r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            "url": r'https?://[^\s]+',
        }
    
    @property
    def domain_name(self) -> str:
        return "pattern"
    
    async def can_handle(self, input_data, context=None):
        if input_data.input_type != "text":
            return False
        
        for pattern in self.patterns.values():
            if re.search(pattern, input_data.content):
                return True
        return False
    
    async def analyze(self, input_data, context=None):
        matches = {}
        for name, pattern in self.patterns.items():
            found = re.findall(pattern, input_data.content)
            if found:
                matches[name] = found
        
        return {"matches": matches}
    
    async def synthesize(self, input_data, context=None, analysis=None):
        matches = analysis.get("matches", {})
        
        summary = []
        for type_, values in matches.items():
            summary.append(f"Found {len(values)} {type}(s)")
        
        return CognitiveResponse(
            content=", ".join(summary),
            confidence=0.95,
            metadata={"matches": matches}
        )
```

---

## Resources

### Documentation
- [Architecture Guide](ARCHITECTURE.md)
- [API Reference](API_GUIDE.md)
- [Quickstart Tutorial](QUICKSTART.md)

### Examples
- `examples/quickstart_template.py` - Minimal working example
- `examples/electronics_repair_example.py` - Advanced domain with memory
- `examples/registry_router_example.py` - Multi-domain orchestration

### Community
- GitHub Issues: Report bugs, request features
- Discussions: Ask questions, share plugins
- Contributing: See CONTRIBUTING.md

---

## Conclusion

You now have everything you need to create powerful cognitive plugins for BlackMamba!

**Remember:**
- Start simple, iterate
- Test thoroughly
- Document your domain
- Share with the community

**Next Steps:**
1. Run `blackmamba new my-domain` to create your first plugin
2. Customize the three core methods
3. Test with real data
4. Deploy and monitor

Happy building! 🚀

---

**BlackMamba Cognitive Core** - Building the Future of Vertical AI 🧠✨
