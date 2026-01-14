"""Unit tests for memory store"""
import pytest
from blackmamba.memory.store import InMemoryStore


@pytest.mark.asyncio
async def test_store_and_retrieve(memory_store):
    """Test storing and retrieving data"""
    key = "test_key"
    value = {"data": "test value", "number": 42}
    
    # Store
    entry_id = await memory_store.store(key, value)
    assert entry_id is not None
    
    # Retrieve
    retrieved = await memory_store.retrieve(entry_id)
    assert retrieved == value


@pytest.mark.asyncio
async def test_store_with_tags(memory_store):
    """Test storing with tags"""
    key = "tagged_entry"
    value = {"content": "test"}
    tags = ["tag1", "tag2"]
    
    entry_id = await memory_store.store(key, value, tags=tags)
    
    # Search by tags
    results = await memory_store.search({"tags": ["tag1"]})
    assert len(results) > 0
    assert any(r["id"] == entry_id for r in results)


@pytest.mark.asyncio
async def test_search_by_tags(memory_store):
    """Test searching by tags"""
    # Store multiple entries
    await memory_store.store("entry1", {"a": 1}, tags=["alpha"])
    await memory_store.store("entry2", {"b": 2}, tags=["beta"])
    await memory_store.store("entry3", {"c": 3}, tags=["alpha", "beta"])
    
    # Search for alpha
    results = await memory_store.search({"tags": ["alpha"]})
    assert len(results) >= 2
    
    # Search for beta
    results = await memory_store.search({"tags": ["beta"]})
    assert len(results) >= 2


@pytest.mark.asyncio
async def test_delete(memory_store):
    """Test deleting entries"""
    key = "to_delete"
    value = {"data": "will be deleted"}
    
    entry_id = await memory_store.store(key, value)
    
    # Delete
    deleted = await memory_store.delete(entry_id)
    assert deleted is True
    
    # Verify deletion
    retrieved = await memory_store.retrieve(entry_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_nonexistent(memory_store):
    """Test deleting non-existent entry"""
    deleted = await memory_store.delete("nonexistent_key")
    assert deleted is False


@pytest.mark.asyncio
async def test_search_content_contains(memory_store):
    """Test searching by content"""
    await memory_store.store("entry1", {"message": "hello world"})
    await memory_store.store("entry2", {"message": "goodbye world"})
    
    results = await memory_store.search({"content_contains": "hello"})
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_get_stats(memory_store):
    """Test getting memory statistics"""
    await memory_store.store("entry1", {"a": 1}, tags=["test"])
    await memory_store.store("entry2", {"b": 2}, tags=["test"])
    
    stats = await memory_store.get_stats()
    assert stats["total_entries"] >= 2
    assert "test" in stats["tags"]


@pytest.mark.asyncio
async def test_access_count(memory_store):
    """Test that access count is tracked"""
    key = "access_test"
    value = {"data": "test"}
    
    entry_id = await memory_store.store(key, value)
    
    # Access multiple times
    await memory_store.retrieve(entry_id)
    await memory_store.retrieve(entry_id)
    await memory_store.retrieve(entry_id)
    
    # Stats should reflect accesses
    stats = await memory_store.get_stats()
    assert stats["total_accesses"] >= 3
