"""
Domain Router - Intelligent routing to domain processors

This module provides routing logic to select the most appropriate domain
processor for a given input based on scoring, priority, and fallback chains.
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging

from blackmamba.core.types import Input, ProcessingContext
from blackmamba.core.interfaces import DomainProcessor
from blackmamba.core.domain_registry import DomainRegistry, DomainHealth


logger = logging.getLogger(__name__)


@dataclass
class RoutingScore:
    """Score and metadata for a routing decision"""
    domain_name: str
    score: float  # 0.0 to 1.0
    can_handle: bool
    priority: int
    health: DomainHealth
    metadata: Dict[str, Any]


class RoutingStrategy:
    """Base class for routing strategies"""
    
    async def score(
        self,
        domain_name: str,
        processor: DomainProcessor,
        input_data: Input,
        context: ProcessingContext,
        priority: int,
        health: DomainHealth,
    ) -> RoutingScore:
        """
        Score a domain processor for the given input
        
        Args:
            domain_name: Name of the domain
            processor: Domain processor instance
            input_data: Input to process
            context: Processing context
            priority: Domain priority from registry
            health: Domain health status
            
        Returns:
            RoutingScore with scoring details
        """
        raise NotImplementedError


class DefaultRoutingStrategy(RoutingStrategy):
    """
    Default routing strategy
    
    Scoring formula:
    - Base score from can_handle (0 or 0.5)
    - Priority bonus (0 to 0.3)
    - Health penalty (0 to -0.2)
    """
    
    async def score(
        self,
        domain_name: str,
        processor: DomainProcessor,
        input_data: Input,
        context: ProcessingContext,
        priority: int,
        health: DomainHealth,
    ) -> RoutingScore:
        """Score a domain using default strategy"""
        
        # Check if can handle
        try:
            can_handle = await processor.can_handle(input_data, context)
        except Exception as e:
            logger.error(f"Error checking can_handle for {domain_name}: {e}")
            can_handle = False
        
        # Base score
        score = 0.5 if can_handle else 0.0
        
        # Priority bonus (normalize to 0-0.3 range, assuming max priority ~10)
        priority_bonus = min(priority / 10.0 * 0.3, 0.3)
        score += priority_bonus
        
        # Health penalty
        health_penalty = 0.0
        if health == DomainHealth.DEGRADED:
            health_penalty = 0.1
        elif health == DomainHealth.UNHEALTHY:
            health_penalty = 0.2
        elif health == DomainHealth.UNKNOWN:
            health_penalty = 0.05
        
        score -= health_penalty
        
        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))
        
        return RoutingScore(
            domain_name=domain_name,
            score=score,
            can_handle=can_handle,
            priority=priority,
            health=health,
            metadata={
                "priority_bonus": priority_bonus,
                "health_penalty": health_penalty,
            }
        )


class DomainRouter:
    """
    Router that selects the most appropriate domain processor
    
    Features:
    - Scoring-based selection
    - Priority handling
    - Health awareness
    - Fallback chains
    - Circuit breaker pattern
    """
    
    def __init__(
        self,
        registry: DomainRegistry,
        strategy: Optional[RoutingStrategy] = None,
    ):
        """
        Initialize the domain router
        
        Args:
            registry: Domain registry instance
            strategy: Routing strategy (defaults to DefaultRoutingStrategy)
        """
        self.registry = registry
        self.strategy = strategy or DefaultRoutingStrategy()
        self._fallback_chains: Dict[str, List[str]] = {}
        self._circuit_breaker_failures: Dict[str, int] = {}
        self._circuit_breaker_threshold = 5
        logger.info("DomainRouter initialized")
    
    def set_fallback_chain(self, primary: str, fallbacks: List[str]):
        """
        Define a fallback chain for a domain
        
        Args:
            primary: Primary domain name
            fallbacks: List of fallback domain names (in order)
        """
        self._fallback_chains[primary] = fallbacks
        logger.info(f"Set fallback chain for {primary}: {fallbacks}")
    
    def get_fallback_chain(self, domain_name: str) -> List[str]:
        """Get the fallback chain for a domain"""
        return self._fallback_chains.get(domain_name, [])
    
    async def route(
        self,
        input_data: Input,
        context: ProcessingContext,
        exclude: Optional[List[str]] = None,
    ) -> Optional[Tuple[str, DomainProcessor, RoutingScore]]:
        """
        Route an input to the most appropriate domain processor
        
        Args:
            input_data: Input to route
            context: Processing context
            exclude: List of domain names to exclude from routing
            
        Returns:
            Tuple of (domain_name, processor, score) or None if no suitable domain
        """
        exclude = exclude or []
        
        # Get all enabled domains
        domain_names = self.registry.list_domains(enabled_only=True)
        
        # Filter out excluded domains and circuit-broken domains
        domain_names = [
            name for name in domain_names
            if name not in exclude
            and not self._is_circuit_broken(name)
        ]
        
        if not domain_names:
            logger.warning("No available domains for routing")
            return None
        
        # Score all domains
        scores: List[RoutingScore] = []
        
        for domain_name in domain_names:
            info = self.registry.get_info(domain_name)
            if not info:
                continue
            
            score = await self.strategy.score(
                domain_name=domain_name,
                processor=info.processor,
                input_data=input_data,
                context=context,
                priority=info.priority,
                health=info.health,
            )
            
            scores.append(score)
        
        # Filter to only domains that can handle
        valid_scores = [s for s in scores if s.can_handle]
        
        if not valid_scores:
            logger.warning(f"No domain can handle input type: {input_data.type}")
            return None
        
        # Sort by score (highest first)
        valid_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Select best domain
        best = valid_scores[0]
        processor = self.registry.get(best.domain_name)
        
        logger.info(
            f"Routed to domain: {best.domain_name} "
            f"(score={best.score:.2f}, priority={best.priority})"
        )
        
        return (best.domain_name, processor, best)
    
    async def route_with_fallback(
        self,
        input_data: Input,
        context: ProcessingContext,
    ) -> Optional[Tuple[str, DomainProcessor, RoutingScore]]:
        """
        Route with automatic fallback chain support
        
        Args:
            input_data: Input to route
            context: Processing context
            
        Returns:
            Tuple of (domain_name, processor, score) or None if all fail
        """
        # Try primary routing
        result = await self.route(input_data, context)
        
        if result:
            domain_name, processor, score = result
            
            # Check if this domain has fallbacks
            fallbacks = self.get_fallback_chain(domain_name)
            
            if fallbacks:
                logger.debug(f"Domain {domain_name} has fallback chain: {fallbacks}")
            
            return result
        
        logger.warning("Primary routing failed, no fallback attempted")
        return None
    
    async def route_all(
        self,
        input_data: Input,
        context: ProcessingContext,
    ) -> List[Tuple[str, DomainProcessor, RoutingScore]]:
        """
        Get all domains that can handle the input, sorted by score
        
        Args:
            input_data: Input to route
            context: Processing context
            
        Returns:
            List of (domain_name, processor, score) tuples
        """
        domain_names = self.registry.list_domains(enabled_only=True)
        
        # Score all domains
        results: List[Tuple[str, DomainProcessor, RoutingScore]] = []
        
        for domain_name in domain_names:
            if self._is_circuit_broken(domain_name):
                continue
                
            info = self.registry.get_info(domain_name)
            if not info:
                continue
            
            score = await self.strategy.score(
                domain_name=domain_name,
                processor=info.processor,
                input_data=input_data,
                context=context,
                priority=info.priority,
                health=info.health,
            )
            
            if score.can_handle:
                results.append((domain_name, info.processor, score))
        
        # Sort by score
        results.sort(key=lambda x: x[2].score, reverse=True)
        
        return results
    
    def record_failure(self, domain_name: str):
        """
        Record a failure for circuit breaker
        
        Args:
            domain_name: Name of the domain that failed
        """
        self._circuit_breaker_failures[domain_name] = \
            self._circuit_breaker_failures.get(domain_name, 0) + 1
        
        failures = self._circuit_breaker_failures[domain_name]
        
        if failures >= self._circuit_breaker_threshold:
            logger.warning(
                f"Circuit breaker opened for {domain_name} "
                f"({failures} failures)"
            )
    
    def record_success(self, domain_name: str):
        """
        Record a success for circuit breaker (resets counter)
        
        Args:
            domain_name: Name of the domain that succeeded
        """
        if domain_name in self._circuit_breaker_failures:
            del self._circuit_breaker_failures[domain_name]
    
    def reset_circuit_breaker(self, domain_name: str):
        """
        Manually reset circuit breaker for a domain
        
        Args:
            domain_name: Name of the domain
        """
        if domain_name in self._circuit_breaker_failures:
            del self._circuit_breaker_failures[domain_name]
            logger.info(f"Reset circuit breaker for {domain_name}")
    
    def _is_circuit_broken(self, domain_name: str) -> bool:
        """Check if circuit breaker is open for a domain"""
        failures = self._circuit_breaker_failures.get(domain_name, 0)
        return failures >= self._circuit_breaker_threshold
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics
        
        Returns:
            Dictionary with router statistics
        """
        return {
            "fallback_chains": self._fallback_chains,
            "circuit_breaker_failures": self._circuit_breaker_failures,
            "circuit_breaker_threshold": self._circuit_breaker_threshold,
            "circuit_broken_domains": [
                name for name in self._circuit_breaker_failures
                if self._is_circuit_broken(name)
            ]
        }
