"""
In-memory store implementation with persistence
"""
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from blackmamba.core.interfaces import MemoryStore
from blackmamba.core.types import MemoryEntry


class InMemoryStore(MemoryStore):
    """Simple in-memory storage with optional file persistence"""
    
    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize memory store
        
        Args:
            persist_path: Optional path to persist memory to disk
        """
        self._storage: Dict[str, MemoryEntry] = {}
        self._persist_path = persist_path
        
        # Load from disk if path provided
        if self._persist_path and os.path.exists(self._persist_path):
            self._load_from_disk()
    
    async def store(
        self,
        key: str,
        value: Dict[str, Any],
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store a value in memory
        
        Args:
            key: Storage key
            value: Value to store
            tags: Optional tags for categorization
            
        Returns:
            ID of the stored entry
        """
        entry_id = key if key.startswith("input_") else str(uuid.uuid4())
        
        entry = MemoryEntry(
            id=entry_id,
            type="memory",
            content=value,
            tags=tags or [],
            related_inputs=[],
            created_at=datetime.utcnow(),
            accessed_count=0
        )
        
        self._storage[entry_id] = entry
        
        # Persist if configured
        if self._persist_path:
            await self._persist_to_disk()
        
        return entry_id
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a value from memory
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None if not found
        """
        if key not in self._storage:
            return None
        
        entry = self._storage[key]
        entry.accessed_count += 1
        entry.last_accessed = datetime.utcnow()
        
        # Persist updated access info
        if self._persist_path:
            await self._persist_to_disk()
        
        return entry.content
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search memory with a query
        
        Args:
            query: Search query (supports 'tags', 'type', 'content_contains')
            
        Returns:
            List of matching entries
        """
        results = []
        
        for entry in self._storage.values():
            if self._matches_query(entry, query):
                results.append({
                    "id": entry.id,
                    "type": entry.type,
                    "content": entry.content,
                    "tags": entry.tags,
                    "created_at": entry.created_at.isoformat(),
                })
        
        return results
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from memory
        
        Args:
            key: Storage key
            
        Returns:
            True if deleted, False if not found
        """
        if key not in self._storage:
            return False
        
        del self._storage[key]
        
        # Persist deletion
        if self._persist_path:
            await self._persist_to_disk()
        
        return True
    
    def _matches_query(self, entry: MemoryEntry, query: Dict[str, Any]) -> bool:
        """Check if an entry matches a query"""
        # Match by tags
        if "tags" in query:
            query_tags = query["tags"] if isinstance(query["tags"], list) else [query["tags"]]
            if not any(tag in entry.tags for tag in query_tags):
                return False
        
        # Match by type
        if "type" in query and entry.type != query["type"]:
            return False
        
        # Match by content (simple string search)
        if "content_contains" in query:
            content_str = json.dumps(entry.content).lower()
            if query["content_contains"].lower() not in content_str:
                return False
        
        return True
    
    async def _persist_to_disk(self):
        """Persist memory to disk"""
        if not self._persist_path:
            return
        
        # Create directory if needed
        os.makedirs(os.path.dirname(self._persist_path), exist_ok=True)
        
        # Convert to serializable format
        data = {
            key: entry.dict()
            for key, entry in self._storage.items()
        }
        
        with open(self._persist_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_from_disk(self):
        """Load memory from disk"""
        if not self._persist_path or not os.path.exists(self._persist_path):
            return
        
        with open(self._persist_path, 'r') as f:
            data = json.load(f)
        
        for key, entry_dict in data.items():
            # Convert datetime strings back to datetime objects
            if "created_at" in entry_dict:
                entry_dict["created_at"] = datetime.fromisoformat(
                    entry_dict["created_at"].replace("Z", "+00:00")
                )
            if "last_accessed" in entry_dict and entry_dict["last_accessed"]:
                entry_dict["last_accessed"] = datetime.fromisoformat(
                    entry_dict["last_accessed"].replace("Z", "+00:00")
                )
            
            self._storage[key] = MemoryEntry(**entry_dict)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_entries": len(self._storage),
            "total_accesses": sum(e.accessed_count for e in self._storage.values()),
            "tags": list(set(tag for e in self._storage.values() for tag in e.tags)),
        }
