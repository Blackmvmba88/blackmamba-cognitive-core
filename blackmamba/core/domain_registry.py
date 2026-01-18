"""
Domain Registry - Dynamic registration and management of domain processors

This module provides hot-plug capability for domain processors, allowing
domains to be registered, unregistered, and health-checked at runtime.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio

from blackmamba.core.interfaces import DomainProcessor


logger = logging.getLogger(__name__)


class DomainHealth(Enum):
    """Health status of a domain"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DomainInfo:
    """Information about a registered domain"""
    processor: DomainProcessor
    registered_at: datetime
    version: str = "1.0.0"
    health: DomainHealth = DomainHealth.UNKNOWN
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0  # Higher priority = checked first by router
    enabled: bool = True


class DomainRegistry:
    """
    Registry for domain processors with hot-plug support
    
    Features:
    - Dynamic registration/unregistration
    - Health checking
    - Dependency tracking
    - Event notifications
    - Priority management
    """

    def __init__(self):
        """Initialize the domain registry"""
        self._domains: Dict[str, DomainInfo] = {}
        self._event_handlers: Dict[str, List[Callable]] = {
            "register": [],
            "unregister": [],
            "health_change": [],
        }
        self._health_check_interval = 60  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        logger.info("DomainRegistry initialized")

    def register(
        self,
        processor: DomainProcessor,
        version: str = "1.0.0",
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register a domain processor
        
        Args:
            processor: Domain processor instance
            version: Semantic version of the domain
            priority: Priority for routing (higher = checked first)
            dependencies: List of domain names this domain depends on
            metadata: Additional metadata about the domain
            
        Returns:
            True if successfully registered, False if already exists
        """
        domain_name = processor.domain_name
        
        if domain_name in self._domains:
            logger.warning(f"Domain {domain_name} already registered")
            return False
        
        # Validate dependencies
        if dependencies:
            missing = [d for d in dependencies if d not in self._domains]
            if missing:
                logger.error(f"Cannot register {domain_name}: missing dependencies {missing}")
                raise ValueError(f"Missing dependencies: {missing}")
        
        # Create domain info
        info = DomainInfo(
            processor=processor,
            registered_at=datetime.utcnow(),
            version=version,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        
        self._domains[domain_name] = info
        logger.info(f"Registered domain: {domain_name} v{version} (priority={priority})")
        
        # Notify handlers
        self._notify_handlers("register", domain_name, info)
        
        return True

    def unregister(self, domain_name: str) -> bool:
        """
        Unregister a domain processor
        
        Args:
            domain_name: Name of the domain to unregister
            
        Returns:
            True if successfully unregistered, False if not found
        """
        if domain_name not in self._domains:
            logger.warning(f"Domain {domain_name} not found")
            return False
        
        # Check if other domains depend on this one
        dependents = [
            name for name, info in self._domains.items()
            if domain_name in info.dependencies
        ]
        
        if dependents:
            logger.error(f"Cannot unregister {domain_name}: required by {dependents}")
            raise ValueError(f"Domain has dependents: {dependents}")
        
        info = self._domains.pop(domain_name)
        logger.info(f"Unregistered domain: {domain_name}")
        
        # Notify handlers
        self._notify_handlers("unregister", domain_name, info)
        
        return True

    def get(self, domain_name: str) -> Optional[DomainProcessor]:
        """
        Get a domain processor by name
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            Domain processor instance or None if not found
        """
        info = self._domains.get(domain_name)
        return info.processor if info and info.enabled else None

    def get_info(self, domain_name: str) -> Optional[DomainInfo]:
        """
        Get full information about a domain
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            DomainInfo instance or None if not found
        """
        return self._domains.get(domain_name)

    def list_domains(self, enabled_only: bool = False) -> List[str]:
        """
        List all registered domain names
        
        Args:
            enabled_only: If True, only return enabled domains
            
        Returns:
            List of domain names
        """
        if enabled_only:
            return [name for name, info in self._domains.items() if info.enabled]
        return list(self._domains.keys())

    def list_by_priority(self, enabled_only: bool = True) -> List[str]:
        """
        List domains sorted by priority (highest first)
        
        Args:
            enabled_only: If True, only return enabled domains
            
        Returns:
            List of domain names sorted by priority
        """
        items = [
            (name, info) for name, info in self._domains.items()
            if not enabled_only or info.enabled
        ]
        sorted_items = sorted(items, key=lambda x: x[1].priority, reverse=True)
        return [name for name, _ in sorted_items]

    def enable(self, domain_name: str) -> bool:
        """Enable a domain"""
        if domain_name not in self._domains:
            return False
        self._domains[domain_name].enabled = True
        logger.info(f"Enabled domain: {domain_name}")
        return True

    def disable(self, domain_name: str) -> bool:
        """Disable a domain (remains registered but won't be used)"""
        if domain_name not in self._domains:
            return False
        self._domains[domain_name].enabled = False
        logger.info(f"Disabled domain: {domain_name}")
        return True

    async def health_check(self, domain_name: str) -> DomainHealth:
        """
        Perform health check on a domain
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            Health status of the domain
        """
        info = self._domains.get(domain_name)
        if not info:
            return DomainHealth.UNKNOWN
        
        try:
            # Try to use the domain processor's health check if it has one
            processor = info.processor
            if hasattr(processor, 'health_check'):
                is_healthy = await processor.health_check()
                new_health = DomainHealth.HEALTHY if is_healthy else DomainHealth.UNHEALTHY
            else:
                # Default: assume healthy if can be called
                new_health = DomainHealth.HEALTHY
            
            old_health = info.health
            info.health = new_health
            info.last_health_check = datetime.utcnow()
            
            if old_health != new_health:
                logger.info(f"Domain {domain_name} health changed: {old_health} -> {new_health}")
                self._notify_handlers("health_change", domain_name, info)
            
            return new_health
            
        except Exception as e:
            logger.error(f"Health check failed for {domain_name}: {e}")
            info.health = DomainHealth.UNHEALTHY
            info.last_health_check = datetime.utcnow()
            return DomainHealth.UNHEALTHY

    async def health_check_all(self) -> Dict[str, DomainHealth]:
        """
        Perform health check on all domains
        
        Returns:
            Dictionary mapping domain names to health status
        """
        results = {}
        for domain_name in self._domains:
            results[domain_name] = await self.health_check(domain_name)
        return results

    def start_health_monitoring(self, interval: int = 60):
        """
        Start periodic health monitoring
        
        Args:
            interval: Health check interval in seconds
        """
        self._health_check_interval = interval
        
        if self._health_check_task and not self._health_check_task.done():
            logger.warning("Health monitoring already running")
            return
        
        async def monitor():
            while True:
                try:
                    await self.health_check_all()
                    await asyncio.sleep(self._health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in health monitoring: {e}")
                    await asyncio.sleep(5)  # Short delay before retry
        
        self._health_check_task = asyncio.create_task(monitor())
        logger.info(f"Started health monitoring (interval={interval}s)")

    def stop_health_monitoring(self):
        """Stop periodic health monitoring"""
        if self._health_check_task:
            self._health_check_task.cancel()
            logger.info("Stopped health monitoring")

    def on_event(self, event_type: str, handler: Callable):
        """
        Register an event handler
        
        Args:
            event_type: Type of event ("register", "unregister", "health_change")
            handler: Callback function(domain_name, domain_info)
        """
        if event_type not in self._event_handlers:
            raise ValueError(f"Unknown event type: {event_type}")
        
        self._event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type} events")

    def _notify_handlers(self, event_type: str, domain_name: str, info: DomainInfo):
        """Notify event handlers"""
        for handler in self._event_handlers.get(event_type, []):
            try:
                handler(domain_name, info)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics
        
        Returns:
            Dictionary with registry statistics
        """
        health_counts = {}
        for info in self._domains.values():
            health = info.health.value
            health_counts[health] = health_counts.get(health, 0) + 1
        
        return {
            "total_domains": len(self._domains),
            "enabled_domains": len([i for i in self._domains.values() if i.enabled]),
            "health_status": health_counts,
            "domains": {
                name: {
                    "version": info.version,
                    "priority": info.priority,
                    "health": info.health.value,
                    "enabled": info.enabled,
                    "dependencies": info.dependencies,
                }
                for name, info in self._domains.items()
            }
        }
