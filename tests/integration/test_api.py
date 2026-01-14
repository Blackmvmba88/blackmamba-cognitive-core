"""Integration tests for the API"""
import pytest
from httpx import ASGITransport, AsyncClient
from blackmamba.api.app import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data
        assert "domains" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_process_text_endpoint():
    """Test text processing endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/process/text",
            json={"text": "Este es un texto de prueba para la API"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response_id" in data
        assert "input_id" in data
        assert "content" in data
        assert "confidence" in data
        assert data["domain"] == "text_analysis"


@pytest.mark.asyncio
async def test_process_text_with_metadata():
    """Test text processing with metadata"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/process/text",
            json={
                "text": "Texto con metadatos",
                "metadata": {"source": "test", "priority": "high"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] > 0


@pytest.mark.asyncio
async def test_process_event_endpoint():
    """Test event processing endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/process/event",
            json={
                "event_type": "user_login",
                "data": {"user_id": "123", "timestamp": "2024-01-01"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response_id" in data
        assert data["domain"] == "event_processing"


@pytest.mark.asyncio
async def test_memory_search_endpoint():
    """Test memory search endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First, process some text to populate memory
        await client.post(
            "/process/text",
            json={"text": "Texto para buscar en memoria"}
        )
        
        # Now search
        response = await client.post(
            "/memory/search",
            json={"tags": ["text"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data


@pytest.mark.asyncio
async def test_memory_stats_endpoint():
    """Test memory statistics endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/memory/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data


@pytest.mark.asyncio
async def test_process_text_error_handling():
    """Test error handling in text processing"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Send invalid request (missing text field)
        response = await client.post(
            "/process/text",
            json={}
        )
        assert response.status_code == 422  # Validation error
