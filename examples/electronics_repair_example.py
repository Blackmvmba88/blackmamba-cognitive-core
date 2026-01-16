"""
Example: Electronics Repair Domain

Demonstrates how to use the electronics repair domain for diagnosing
and tracking repair of electronic boards.
"""

import asyncio
import json
from blackmamba.core.engine import CognitiveEngine
from blackmamba.core.input_processor import InputProcessor
from blackmamba.core.response_generator import ResponseGenerator
from blackmamba.memory.technical_store import TechnicalMemoryStore
from blackmamba.domains.electronics_repair import ElectronicsRepairDomain
from blackmamba.core.technical_types import (
    RepairOutcome,
    RepairAction,
    RepairActionType,
    OutcomeStatus,
)


async def main():
    """Demonstrate electronics repair workflow"""
    
    print("=" * 80)
    print("Electronics Repair Domain Example")
    print("=" * 80)
    print()
    
    # Initialize components
    processor = InputProcessor()
    engine = CognitiveEngine(input_processor=processor)
    technical_memory = TechnicalMemoryStore(persist_path="./data/example_technical_memory.json")
    
    # Register electronics repair domain
    engine.register_domain_processor(ElectronicsRepairDomain())
    
    print("✓ System initialized with Electronics Repair Domain")
    print()
    
    # Scenario 1: Measurement Event
    print("-" * 80)
    print("SCENARIO 1: Voltage Measurement Issue")
    print("-" * 80)
    
    measurement_event = await processor.process_event(
        event_type="measurement",
        event_data={
            "board": "ESP32",
            "measurement_type": "voltage",
            "value": 3.1,
            "expected": 5.0,
            "unit": "V",
            "location": "VCC"
        }
    )
    
    response = await engine.process(measurement_event)
    case_id = response.content.get("case_id")
    
    print(f"\n📊 Input: Voltage measurement on ESP32")
    print(f"   Measured: 3.1V")
    print(f"   Expected: 5.0V")
    print(f"   Location: VCC")
    print(f"\n🔍 Diagnosis:")
    print(f"   Case ID: {case_id}")
    print(f"   Confidence: {response.confidence:.2f}")
    print(f"   Suspected Faults: {response.content['diagnosis']['suspected_faults']}")
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(response.content['recommendations'], 1):
        print(f"   {i}. {rec['action'].replace('_', ' ').title()}")
        print(f"      Reason: {rec['reason']}")
        print(f"      Priority: {rec['priority']}")
    
    print(f"\n📝 Next Steps:")
    for i, step in enumerate(response.content['next_steps'], 1):
        print(f"   {i}. {step}")
    
    # Store case in technical memory
    await technical_memory.store(
        key=f"case_{case_id}",
        value=response.content,
        tags=["diagnostic_case", "ESP32"] + response.content['diagnosis']['suspected_faults']
    )
    
    # Scenario 2: Text Symptom
    print("\n" + "-" * 80)
    print("SCENARIO 2: Text Symptom Description")
    print("-" * 80)
    
    text_input = await processor.process_text(
        text="ESP32 no arranca después de flashear firmware",
        metadata={"source": "technician_report"}
    )
    
    response2 = await engine.process(text_input)
    case_id_2 = response2.content.get("case_id")
    
    print(f"\n📝 Input: 'ESP32 no arranca después de flashear firmware'")
    print(f"\n🔍 Diagnosis:")
    print(f"   Case ID: {case_id_2}")
    print(f"   Confidence: {response2.confidence:.2f}")
    print(f"   Board Type: {response2.content['board_type']}")
    print(f"   Suspected Faults: {response2.content['diagnosis']['suspected_faults']}")
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(response2.content['recommendations'][:3], 1):
        print(f"   {i}. {rec['action'].replace('_', ' ').title()}")
    
    # Scenario 3: Report Outcome
    print("\n" + "-" * 80)
    print("SCENARIO 3: Report Repair Outcome (Learning)")
    print("-" * 80)
    
    # Simulate repair was successful
    outcome = RepairOutcome(
        case_id=case_id,
        actions_taken=[
            RepairAction(
                action_type=RepairActionType.CHECK_CONNECTION,
                description="Checked VCC connection",
                target_location="VCC",
                estimated_time_minutes=5
            ),
            RepairAction(
                action_type=RepairActionType.RESOLDER,
                description="Resoldered VCC pin",
                target_location="VCC",
                estimated_time_minutes=10
            )
        ],
        status=OutcomeStatus.SUCCESS,
        actual_time_minutes=15,
        actual_cost=5.0,
        notes="Cold solder joint on VCC was the root cause",
        success_indicators={
            "voltage_restored": True,
            "device_boots": True
        }
    )
    
    outcome_id = await technical_memory.store_outcome(outcome)
    
    print(f"\n✅ Repair Completed Successfully")
    print(f"   Outcome ID: {outcome_id}")
    print(f"   Actions Taken: Check Connection → Resolder")
    print(f"   Time: 15 minutes")
    print(f"   Cost: $5.00")
    print(f"   Root Cause: Cold solder joint")
    
    # Scenario 4: Query Statistics
    print("\n" + "-" * 80)
    print("SCENARIO 4: Technical Memory Statistics")
    print("-" * 80)
    
    stats = await technical_memory.get_technical_stats()
    
    print(f"\n📈 Technical Memory Stats:")
    print(f"   Total Cases: {stats['total_cases']}")
    print(f"   Total Outcomes: {stats['total_outcomes']}")
    print(f"   Overall Success Rate: {stats['overall_success_rate']:.1%}")
    
    if stats['fault_distribution']:
        print(f"\n   Fault Distribution:")
        for fault, count in sorted(stats['fault_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {fault}: {count}")
    
    if stats['board_distribution']:
        print(f"\n   Board Distribution:")
        for board, count in sorted(stats['board_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
            print(f"      {board}: {count}")
    
    print(f"\n   Patterns Learned: {stats['patterns_learned']}")
    
    # Scenario 5: Query Action Success Rate
    print("\n" + "-" * 80)
    print("SCENARIO 5: Action Success Rate Query")
    print("-" * 80)
    
    action_stats = await technical_memory.get_action_success_rate(
        action_type=RepairActionType.RESOLDER
    )
    
    print(f"\n🎯 Success Rate for '{action_stats['action_type']}':")
    print(f"   Total Cases: {action_stats['total_cases']}")
    print(f"   Successful: {action_stats['successful_cases']}")
    print(f"   Success Rate: {action_stats['success_rate']:.1%}")
    
    # Scenario 6: Find Similar Cases
    print("\n" + "-" * 80)
    print("SCENARIO 6: Find Similar Past Cases")
    print("-" * 80)
    
    from blackmamba.core.technical_types import BoardType, FaultType
    
    similar_cases = await technical_memory.find_similar_cases(
        board_type=BoardType.ESP32,
        suspected_faults=[FaultType.LOW_VOLTAGE],
        limit=3
    )
    
    print(f"\n🔍 Similar Cases for ESP32 with low_voltage fault:")
    print(f"   Found: {len(similar_cases)} similar case(s)")
    
    for i, case_data in enumerate(similar_cases, 1):
        print(f"\n   Case {i}:")
        print(f"      Similarity Score: {case_data['similarity_score']:.2f}")
        if case_data.get('outcome'):
            print(f"      Outcome: {case_data['outcome'].get('status', 'unknown')}")
            actions = case_data['outcome'].get('actions_taken', [])
            if actions:
                print(f"      Actions: {', '.join([a.get('action_type', '') for a in actions])}")
    
    print("\n" + "=" * 80)
    print("✨ Example completed successfully!")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("• The system can process both structured measurements and text descriptions")
    print("• Diagnostics include confidence scores and actionable recommendations")
    print("• Outcomes are tracked for continuous learning")
    print("• Similar cases can be queried to leverage past experience")
    print("• Success rates help prioritize repair actions")
    print()
    print("This demonstrates an OPERATIONAL AI that:")
    print("  Senses → Diagnoses → Acts → Remembers → Improves")
    print()


if __name__ == "__main__":
    asyncio.run(main())
