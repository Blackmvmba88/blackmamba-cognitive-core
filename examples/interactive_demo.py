#!/usr/bin/env python3
"""
BlackMamba Cognitive Core - Interactive Demo
============================================

An end-to-end demonstration showing the full cognitive cycle:
- Sensing (measurements from electronic boards)
- Diagnosis (intelligent fault detection)
- Recommendation (actionable repair steps)
- Learning (outcome tracking and pattern improvement)

This demo can be recorded or shown live to demonstrate capabilities.
"""

import asyncio
import sys
from typing import List, Dict, Any
from datetime import datetime


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_step(step_num: int, title: str):
    """Print a step header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}[Step {step_num}] {title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")


def print_info(text: str):
    """Print informational text"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_data(label: str, value: Any, indent: int = 2):
    """Print data with label"""
    spaces = " " * indent
    print(f"{spaces}{Colors.BOLD}{label}:{Colors.ENDC} {value}")


async def pause(seconds: float = 1.5):
    """Pause for effect in demo"""
    await asyncio.sleep(seconds)


async def wait_for_user():
    """Wait for user to press Enter"""
    print(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
    await asyncio.get_event_loop().run_in_executor(None, input)


async def demo_scenario_1():
    """Scenario 1: ESP32 Board with Low Voltage"""
    print_step(1, "Scenario: ESP32 Board Not Booting")
    
    print_info("A technician has an ESP32 board that won't boot.")
    print_info("First step: Measure voltage at VCC pin")
    await pause()
    
    # Import here to show real-time loading
    print_info("Initializing cognitive engine...")
    from blackmamba.core.engine import CognitiveEngine
    from blackmamba.core.input_processor import InputProcessor
    from blackmamba.domains.electronics_repair import ElectronicsRepairDomain
    from blackmamba.memory.technical_store import TechnicalMemoryStore
    
    # Initialize system
    processor = InputProcessor()
    memory = TechnicalMemoryStore()
    engine = CognitiveEngine(input_processor=processor)
    engine.register_domain_processor(ElectronicsRepairDomain(memory_store=memory))
    
    print_success("Cognitive engine initialized with Electronics Repair domain")
    await pause()
    
    # Simulate measurement
    print("\n📊 Measurement Data:")
    print_data("Board Type", "ESP32", 2)
    print_data("Location", "VCC Pin", 2)
    print_data("Expected Voltage", "5.0V", 2)
    print_data("Measured Voltage", "3.1V", 2)
    print_warning("Voltage is below expected threshold!")
    await pause()
    
    # Process measurement
    print_info("Sending measurement to cognitive engine...")
    input_data = await processor.process_event({
        "event_type": "measurement",
        "board_type": "ESP32",
        "measurement_type": "voltage",
        "value": 3.1,
        "expected_value": 5.0,
        "unit": "V",
        "location": "VCC",
        "symptoms": ["board_not_booting", "no_power"]
    })
    
    response = await engine.process(input_data)
    await pause()
    
    # Show diagnosis
    print("\n🔍 Diagnostic Results:")
    if response.metadata and "diagnosis" in response.metadata:
        diagnosis = response.metadata["diagnosis"]
        print_data("Case ID", diagnosis.get("case_id", "N/A")[:8] + "...", 2)
        print_data("Confidence", f"{diagnosis.get('confidence', 0)*100:.1f}%", 2)
        
        if "suspected_faults" in diagnosis:
            print(f"\n  {Colors.BOLD}Suspected Faults:{Colors.ENDC}")
            for fault in diagnosis["suspected_faults"]:
                print(f"    • {fault.replace('_', ' ').title()}")
    
    await pause()
    
    # Show recommendations
    if response.metadata and "recommendations" in response.metadata:
        print("\n🔧 Recommended Actions:")
        for i, rec in enumerate(response.metadata["recommendations"][:3], 1):
            priority_color = Colors.RED if rec.get("priority") == "high" else Colors.YELLOW
            print(f"  {i}. {rec.get('action_type', 'unknown').replace('_', ' ').title()}")
            print(f"     {priority_color}Priority: {rec.get('priority', 'medium').upper()}{Colors.ENDC}")
            if "reason" in rec:
                print(f"     Reason: {rec['reason']}")
    
    await pause()
    return response.metadata.get("diagnosis", {}).get("case_id") if response.metadata else None


async def demo_scenario_2(case_id: str):
    """Scenario 2: Report Successful Repair"""
    print_step(2, "Scenario: Repair Execution & Outcome")
    
    print_info("The technician follows the recommendations...")
    await pause()
    
    print("\n🔨 Actions Taken:")
    print_data("Action 1", "Checked VCC connection - found loose wire", 2)
    print_data("Action 2", "Resoldered VCC pin", 2)
    print_data("Action 3", "Re-measured voltage - now 5.0V", 2)
    print_data("Time Taken", "15 minutes", 2)
    await pause()
    
    print_success("Board now boots successfully!")
    await pause()
    
    # Report outcome for learning
    print_info("Reporting outcome to cognitive system for learning...")
    from blackmamba.core.input_processor import InputProcessor
    from blackmamba.core.engine import CognitiveEngine
    from blackmamba.domains.electronics_repair import ElectronicsRepairDomain
    from blackmamba.memory.technical_store import TechnicalMemoryStore
    
    processor = InputProcessor()
    memory = TechnicalMemoryStore()
    engine = CognitiveEngine(input_processor=processor)
    engine.register_domain_processor(ElectronicsRepairDomain(memory_store=memory))
    
    input_data = await processor.process_event({
        "event_type": "outcome",
        "case_id": case_id,
        "status": "success",
        "resolution_time_minutes": 15,
        "actions_taken": [
            {
                "action_type": "check_connection",
                "success": True,
                "notes": "Found loose wire at VCC"
            },
            {
                "action_type": "resolder",
                "success": True,
                "notes": "Resoldered VCC pin"
            }
        ]
    })
    
    await engine.process(input_data)
    await pause()
    
    print_success("Outcome recorded! System will learn from this case.")
    print_info("Future similar cases will benefit from this experience.")


async def demo_scenario_3():
    """Scenario 3: Query Similar Cases"""
    print_step(3, "Scenario: Learning from History")
    
    print_info("Let's see what the system has learned...")
    await pause()
    
    from blackmamba.memory.technical_store import TechnicalMemoryStore
    
    memory = TechnicalMemoryStore()
    
    # Get stats
    stats = await memory.get_stats()
    
    print("\n📈 Memory Statistics:")
    print_data("Total Cases", stats.get("total_cases", 0), 2)
    print_data("Successful Repairs", stats.get("successful_cases", 0), 2)
    print_data("Known Patterns", stats.get("pattern_count", 0), 2)
    await pause()
    
    # Query similar cases
    print_info("Querying similar cases with low voltage on ESP32...")
    similar = await memory.find_similar_cases(
        board_type="ESP32",
        symptoms=["low_voltage"],
        limit=3
    )
    
    if similar:
        print(f"\n🔎 Found {len(similar)} similar case(s):")
        for i, case in enumerate(similar, 1):
            print(f"\n  Case {i}:")
            print_data("Board", case.get("board_type", "Unknown"), 4)
            print_data("Outcome", case.get("outcome", {}).get("status", "Unknown"), 4)
            if "pattern_id" in case:
                print_data("Pattern ID", case["pattern_id"][:8] + "...", 4)
    else:
        print_warning("No similar cases found yet. System will learn from more cases.")
    
    await pause()


async def demo_cognitive_loop():
    """Demonstrate the complete cognitive loop"""
    print_step(4, "The Cognitive Loop")
    
    print_info("BlackMamba implements a complete cognitive cycle:")
    await pause(0.5)
    
    print(f"\n  {Colors.BOLD}1. SENSE{Colors.ENDC} → Receive measurements and symptoms")
    await pause(0.5)
    print(f"  {Colors.BOLD}2. ANALYZE{Colors.ENDC} → Diagnose using knowledge base + patterns")
    await pause(0.5)
    print(f"  {Colors.BOLD}3. DECIDE{Colors.ENDC} → Generate prioritized recommendations")
    await pause(0.5)
    print(f"  {Colors.BOLD}4. ACT{Colors.ENDC} → Provide actionable guidance")
    await pause(0.5)
    print(f"  {Colors.BOLD}5. REMEMBER{Colors.ENDC} → Store outcomes and learn patterns")
    await pause(0.5)
    print(f"  {Colors.BOLD}6. IMPROVE{Colors.ENDC} → Update knowledge from experience")
    await pause()
    
    print_success("This creates a self-improving system!")


async def demo_platform_vision():
    """Show the platform vision"""
    print_step(5, "Platform Vision: Cognitive Plugins")
    
    print_info("BlackMamba is designed as a platform, not just a tool.")
    await pause()
    
    print(f"\n  {Colors.BOLD}Current Domain:{Colors.ENDC} Electronics Repair")
    print("    • Diagnose PCB faults")
    print("    • Recommend repair actions")
    print("    • Learn from outcomes")
    await pause()
    
    print(f"\n  {Colors.BOLD}Potential Domains (same engine):{Colors.ENDC}")
    print("    • Industrial Maintenance")
    print("    • Automotive Diagnostics")
    print("    • Home Automation")
    print("    • Medical Equipment")
    print("    • Supply Chain Optimization")
    await pause()
    
    print(f"\n  {Colors.CYAN}Each domain is a plugin - same cognitive architecture!{Colors.ENDC}")


async def main():
    """Main demo execution"""
    print_header("BlackMamba Cognitive Core - Interactive Demo")
    
    print(f"{Colors.BOLD}Welcome to BlackMamba!{Colors.ENDC}")
    print("An end-to-end cognitive platform for vertical AI applications.\n")
    print("This demo shows a complete cycle:")
    print("  • Real-world problem (electronics repair)")
    print("  • Intelligent diagnosis")
    print("  • Actionable recommendations")
    print("  • Learning from outcomes")
    
    await wait_for_user()
    
    try:
        # Run scenarios
        case_id = await demo_scenario_1()
        await wait_for_user()
        
        if case_id:
            await demo_scenario_2(case_id)
            await wait_for_user()
        
        await demo_scenario_3()
        await wait_for_user()
        
        await demo_cognitive_loop()
        await wait_for_user()
        
        await demo_platform_vision()
        
        # Finale
        print_header("Demo Complete!")
        print_success("You've seen the complete cognitive cycle in action.")
        print_info("BlackMamba transforms from motor cognitivo → plataforma vertical")
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print("  1. Try the quickstart: python examples/quickstart_template.py")
        print("  2. Create your own domain: blackmamba new my-domain")
        print("  3. Read the docs: docs/PLUGIN_DEVELOPMENT_GUIDE.md")
        print(f"\n{Colors.CYAN}Thank you for exploring BlackMamba!{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user.{Colors.ENDC}\n")
    except Exception as e:
        print_error(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
