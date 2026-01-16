"""
Technical memory store for electronics repair cases

Extends the base memory store with technical-specific functionality:
- Case storage and retrieval
- Pattern matching for similar cases
- Success rate tracking
- Temporal analysis
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from blackmamba.memory.store import InMemoryStore
from blackmamba.core.technical_types import (
    DiagnosticCase,
    RepairOutcome,
    TechnicalPattern,
    FaultType,
    BoardType,
    OutcomeStatus,
    RepairActionType,
)


class TechnicalMemoryStore(InMemoryStore):
    """
    Extended memory store for technical repair cases
    
    Adds capabilities for:
    - Storing diagnostic cases with outcomes
    - Finding similar past cases
    - Tracking repair action success rates
    - Learning patterns from historical data
    """
    
    def __init__(self, persist_path: Optional[str] = None):
        super().__init__(persist_path)
        self._patterns: Dict[str, TechnicalPattern] = {}
    
    async def store(self, key: str, value: Dict[str, Any], tags: Optional[List[str]] = None) -> str:
        """
        Override store to use the provided key directly for case_ and outcome_ prefixed keys
        
        Args:
            key: Storage key
            value: Value to store
            tags: Optional tags for categorization
            
        Returns:
            ID of the stored entry
        """
        # Use the key directly if it starts with case_ or outcome_
        if key.startswith("case_") or key.startswith("outcome_"):
            entry_id = key
        else:
            entry_id = key if key.startswith("input_") else str(uuid.uuid4())
        
        from blackmamba.core.types import MemoryEntry
        entry = MemoryEntry(
            id=entry_id,
            type="memory",
            content=value,
            tags=tags or [],
            related_inputs=[],
            created_at=datetime.now(timezone.utc),
            accessed_count=0,
        )
        
        self._storage[entry_id] = entry
        
        # Persist if configured
        if self._persist_path:
            await self._persist_to_disk()
        
        return entry_id
    
    async def store_case(self, case: DiagnosticCase) -> str:
        """
        Store a diagnostic case
        
        Args:
            case: Diagnostic case to store
            
        Returns:
            Case ID
        """
        case_dict = case.model_dump()
        case_key = f"case_{case.id}"
        await self.store(
            key=case_key,
            value=case_dict,
            tags=["diagnostic_case", case.board_type.value] + [f.value for f in case.suspected_faults]
        )
        return case_key
    
    async def store_outcome(self, outcome: RepairOutcome) -> str:
        """
        Store a repair outcome and update patterns
        
        Args:
            outcome: Repair outcome to store
            
        Returns:
            Outcome ID
        """
        outcome_dict = outcome.model_dump()
        outcome_key = f"outcome_{outcome.case_id}"
        await self.store(
            key=outcome_key,
            value=outcome_dict,
            tags=["repair_outcome", outcome.status.value, outcome.case_id]
        )
        
        # Update patterns based on outcome
        await self._update_patterns(outcome)
        
        return outcome_key
    
    async def find_similar_cases(
        self, 
        board_type: BoardType, 
        suspected_faults: List[FaultType],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar past cases based on board type and faults
        
        Args:
            board_type: Type of board
            suspected_faults: List of suspected faults
            limit: Maximum number of results
            
        Returns:
            List of similar cases with their outcomes
        """
        # Search for cases with matching board type
        cases = await self.search({
            "tags": board_type.value,
            "type": "memory"
        })
        
        # Score and rank by similarity
        scored_cases = []
        for case in cases:
            if "suspected_faults" in case["content"]:
                case_faults = case["content"]["suspected_faults"]
                # Calculate overlap score
                overlap = len(set(case_faults) & set([f.value for f in suspected_faults]))
                if overlap > 0:
                    score = overlap / max(len(case_faults), len(suspected_faults))
                    scored_cases.append((score, case))
        
        # Sort by score and return top results
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        results = []
        
        for score, case in scored_cases[:limit]:
            # Try to find associated outcome
            outcome = await self.retrieve(f"outcome_{case['id'].replace('case_', '')}")
            results.append({
                "case": case,
                "outcome": outcome,
                "similarity_score": score
            })
        
        return results
    
    async def get_action_success_rate(
        self, 
        action_type: RepairActionType,
        fault_type: Optional[FaultType] = None,
        board_type: Optional[BoardType] = None
    ) -> Dict[str, Any]:
        """
        Calculate success rate for a specific repair action
        
        Args:
            action_type: Type of repair action
            fault_type: Optional fault type filter
            board_type: Optional board type filter
            
        Returns:
            Success rate statistics
        """
        # Find all outcomes
        outcomes = await self.search({"tags": "repair_outcome"})
        
        total = 0
        successful = 0
        
        for outcome_data in outcomes:
            outcome_content = outcome_data["content"]
            
            # Check if this outcome used the action
            actions = outcome_content.get("actions_taken", [])
            has_action = any(
                action.get("action_type") == action_type.value 
                for action in actions
            )
            
            if not has_action:
                continue
            
            # Apply filters if provided
            if fault_type or board_type:
                # Get associated case
                case_id = outcome_content.get("case_id")
                case = await self.retrieve(f"case_{case_id}")
                if not case:
                    continue
                
                if fault_type and fault_type.value not in case.get("suspected_faults", []):
                    continue
                
                if board_type and case.get("board_type") != board_type.value:
                    continue
            
            total += 1
            if outcome_content.get("status") == OutcomeStatus.SUCCESS.value:
                successful += 1
        
        return {
            "action_type": action_type.value,
            "total_cases": total,
            "successful_cases": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "filters": {
                "fault_type": fault_type.value if fault_type else None,
                "board_type": board_type.value if board_type else None
            }
        }
    
    async def get_pattern(self, fault_type: FaultType) -> Optional[TechnicalPattern]:
        """
        Get learned pattern for a fault type
        
        Args:
            fault_type: Type of fault
            
        Returns:
            Pattern if available
        """
        pattern_key = f"pattern_{fault_type.value}"
        if pattern_key in self._patterns:
            return self._patterns[pattern_key]
        
        # Try to generate pattern from stored cases
        return await self._generate_pattern(fault_type)
    
    async def _update_patterns(self, outcome: RepairOutcome):
        """
        Update patterns based on a new outcome
        
        This is where the system "learns" from experience
        """
        # Normalize case_id to ensure it has case_ prefix
        case_id = outcome.case_id if outcome.case_id.startswith("case_") else f"case_{outcome.case_id}"
        case = await self.retrieve(case_id)
        
        if not case:
            return
        
        # Update patterns for each fault type in the case
        for fault_str in case.get("suspected_faults", []):
            try:
                # Handle both string values and enum values
                if isinstance(fault_str, str):
                    fault_type = FaultType(fault_str)
                else:
                    fault_type = fault_str
                await self._update_fault_pattern(fault_type, case, outcome)
            except (ValueError, AttributeError):
                # Skip invalid fault types
                continue
    
    def _calculate_success_rate(self, current_rate: float, sample_size: int, is_success: bool) -> float:
        """
        Calculate updated success rate using weighted average
        
        Args:
            current_rate: Current success rate (0.0 - 1.0)
            sample_size: Total sample size including new entry
            is_success: Whether the new entry is a success
            
        Returns:
            Updated success rate
        """
        if sample_size <= 0:
            return 0.0
        
        new_value = 1.0 if is_success else 0.0
        return (current_rate * (sample_size - 1) + new_value) / sample_size
    
    async def _update_fault_pattern(
        self, 
        fault_type: FaultType, 
        case: Dict[str, Any], 
        outcome: RepairOutcome
    ):
        """Update pattern for a specific fault type"""
        pattern_key = f"pattern_{fault_type.value}"
        
        # Get or create pattern
        if pattern_key in self._patterns:
            pattern = self._patterns[pattern_key]
        else:
            pattern = TechnicalPattern(
                pattern_id=pattern_key,
                fault_type=fault_type,
                common_symptoms=[],
                common_measurements={},
                recommended_actions=[],
                success_rate=0.0,
                sample_size=0,
                board_types=[]
            )
        
        # Update pattern with new data
        pattern.sample_size += 1
        
        # Add board type if not present
        board_type = BoardType(case.get("board_type", BoardType.UNKNOWN.value))
        if board_type not in pattern.board_types:
            pattern.board_types.append(board_type)
        
        # Update success rate using helper method
        is_success = outcome.status == OutcomeStatus.SUCCESS
        pattern.success_rate = self._calculate_success_rate(
            pattern.success_rate, 
            pattern.sample_size, 
            is_success
        )
        
        # Add common symptoms
        for symptom in case.get("symptoms", []):
            symptom_desc = symptom.get("description") if isinstance(symptom, dict) else symptom
            if symptom_desc and symptom_desc not in pattern.common_symptoms:
                pattern.common_symptoms.append(symptom_desc)
        
        # Update recommended actions based on successful outcomes
        if outcome.status == OutcomeStatus.SUCCESS:
            for action in outcome.actions_taken:
                # Handle both object and dict representations safely
                if hasattr(action, 'action_type'):
                    action_type = action.action_type
                elif isinstance(action, dict) and 'action_type' in action:
                    action_type = RepairActionType(action['action_type'])
                else:
                    continue  # Skip malformed actions
                
                if action_type not in pattern.recommended_actions:
                    pattern.recommended_actions.append(action_type)
        
        pattern.last_updated = datetime.now(timezone.utc)
        self._patterns[pattern_key] = pattern
    
    async def _generate_pattern(self, fault_type: FaultType) -> Optional[TechnicalPattern]:
        """Generate a pattern from historical cases"""
        # Search for cases with this fault
        cases = await self.search({
            "tags": fault_type.value,
            "type": "memory"
        })
        
        if not cases:
            return None
        
        pattern = TechnicalPattern(
            pattern_id=f"pattern_{fault_type.value}",
            fault_type=fault_type,
            common_symptoms=[],
            common_measurements={},
            recommended_actions=[],
            success_rate=0.0,
            sample_size=len(cases)
        )
        
        # Aggregate data from cases
        symptom_counts = {}
        action_success = {}
        board_types_set = set()
        
        for case_data in cases:
            case = case_data["content"]
            
            # Collect symptoms
            for symptom in case.get("symptoms", []):
                symptom_desc = symptom.get("description") if isinstance(symptom, dict) else str(symptom)
                symptom_counts[symptom_desc] = symptom_counts.get(symptom_desc, 0) + 1
            
            # Collect board types
            board_types_set.add(case.get("board_type", BoardType.UNKNOWN.value))
            
            # Get outcome if available
            case_id = case_data["id"].replace("case_", "")
            outcome = await self.retrieve(f"outcome_{case_id}")
            if outcome:
                for action in outcome.get("actions_taken", []):
                    action_type = action.get("action_type")
                    if action_type not in action_success:
                        action_success[action_type] = {"success": 0, "total": 0}
                    
                    action_success[action_type]["total"] += 1
                    if outcome.get("status") == OutcomeStatus.SUCCESS.value:
                        action_success[action_type]["success"] += 1
        
        # Set most common symptoms
        pattern.common_symptoms = sorted(symptom_counts, key=symptom_counts.get, reverse=True)[:5]
        
        # Set board types
        pattern.board_types = [BoardType(bt) for bt in board_types_set]
        
        # Set recommended actions (sorted by success rate)
        sorted_actions = sorted(
            action_success.items(),
            key=lambda x: x[1]["success"] / x[1]["total"] if x[1]["total"] > 0 else 0,
            reverse=True
        )
        pattern.recommended_actions = [
            RepairActionType(action_type) 
            for action_type, _ in sorted_actions[:5]
        ]
        
        # Calculate overall success rate
        total_outcomes = sum(stats["total"] for stats in action_success.values())
        total_successes = sum(stats["success"] for stats in action_success.values())
        pattern.success_rate = total_successes / total_outcomes if total_outcomes > 0 else 0.0
        
        self._patterns[pattern.pattern_id] = pattern
        return pattern
    
    async def get_technical_stats(self) -> Dict[str, Any]:
        """Get statistics specific to technical memory"""
        base_stats = await self.get_stats()
        
        # Count cases and outcomes
        cases = await self.search({"tags": "diagnostic_case"})
        outcomes = await self.search({"tags": "repair_outcome"})
        
        # Count by fault type
        fault_counts = {}
        for case in cases:
            for fault in case["content"].get("suspected_faults", []):
                fault_counts[fault] = fault_counts.get(fault, 0) + 1
        
        # Count by board type
        board_counts = {}
        for case in cases:
            board = case["content"].get("board_type", "unknown")
            board_counts[board] = board_counts.get(board, 0) + 1
        
        # Calculate success rate
        successful_outcomes = [o for o in outcomes if o["content"].get("status") == OutcomeStatus.SUCCESS.value]
        success_rate = len(successful_outcomes) / len(outcomes) if outcomes else 0.0
        
        return {
            **base_stats,
            "total_cases": len(cases),
            "total_outcomes": len(outcomes),
            "overall_success_rate": success_rate,
            "fault_distribution": fault_counts,
            "board_distribution": board_counts,
            "patterns_learned": len(self._patterns)
        }
