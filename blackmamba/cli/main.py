#!/usr/bin/env python3
"""
BlackMamba CLI - Command Line Interface
Provides tools for creating and managing cognitive domains
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from blackmamba.cli.templates import (
    DOMAIN_TEMPLATE,
    EXAMPLE_TEMPLATE,
    TEST_TEMPLATE,
    README_TEMPLATE,
)


def to_snake_case(name: str) -> str:
    """Convert name to snake_case"""
    import re
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower().replace('-', '_').replace(' ', '_')


def to_pascal_case(name: str) -> str:
    """Convert name to PascalCase"""
    parts = name.replace('-', '_').replace(' ', '_').split('_')
    return ''.join(word.capitalize() for word in parts)


def to_title_case(name: str) -> str:
    """Convert name to Title Case"""
    return name.replace('_', ' ').replace('-', ' ').title()


def create_domain(
    name: str,
    description: str = "Custom cognitive domain",
    base_path: Optional[Path] = None,
) -> bool:
    """
    Create a new cognitive domain from template
    
    Args:
        name: Domain name (will be converted to snake_case)
        description: Brief description of what the domain does
        base_path: Base path for the project (default: current directory)
        
    Returns:
        True if successful, False otherwise
    """
    if base_path is None:
        base_path = Path.cwd()
    
    # Normalize names
    domain_name = to_snake_case(name)
    domain_class_name = to_pascal_case(name)
    domain_name_display = to_title_case(name)
    
    print(f"🚀 Creating new domain: {domain_name_display}")
    print(f"   Domain name: {domain_name}")
    print(f"   Class name: {domain_class_name}Domain")
    
    # Create directory structure
    domains_dir = base_path / "blackmamba" / "domains"
    examples_dir = base_path / "examples"
    tests_dir = base_path / "tests" / "unit"
    
    # Check if directories exist
    if not domains_dir.exists():
        print(f"⚠️  Warning: {domains_dir} does not exist. Creating it...")
        domains_dir.mkdir(parents=True, exist_ok=True)
    
    if not examples_dir.exists():
        examples_dir.mkdir(parents=True, exist_ok=True)
    
    if not tests_dir.exists():
        tests_dir.mkdir(parents=True, exist_ok=True)
    
    # File paths
    domain_file = domains_dir / f"{domain_name}.py"
    example_file = examples_dir / f"{domain_name}_example.py"
    test_file = tests_dir / f"test_{domain_name}.py"
    readme_file = domains_dir / f"{domain_name.upper()}_README.md"
    
    # Check if domain already exists
    if domain_file.exists():
        print(f"❌ Error: Domain {domain_name} already exists at {domain_file}")
        return False
    
    # Template variables
    template_vars = {
        "domain_name": domain_name,
        "domain_class_name": domain_class_name,
        "domain_name_display": domain_name_display,
        "domain_module": f"blackmamba.domains.{domain_name}",
        "description": description,
    }
    
    # Create domain file
    print(f"   Creating domain: {domain_file}")
    with open(domain_file, 'w') as f:
        f.write(DOMAIN_TEMPLATE.format(**template_vars))
    
    # Create example file
    print(f"   Creating example: {example_file}")
    with open(example_file, 'w') as f:
        f.write(EXAMPLE_TEMPLATE.format(**template_vars))
    
    # Create test file
    print(f"   Creating tests: {test_file}")
    with open(test_file, 'w') as f:
        f.write(TEST_TEMPLATE.format(**template_vars))
    
    # Create README
    print(f"   Creating README: {readme_file}")
    with open(readme_file, 'w') as f:
        f.write(README_TEMPLATE.format(**template_vars))
    
    # Success message
    print("\n✅ Domain created successfully!")
    print("\n📝 Next steps:")
    print(f"   1. Edit the domain: {domain_file}")
    print(f"   2. Customize can_handle(), analyze(), and synthesize() methods")
    print(f"   3. Run the example: python {example_file}")
    print(f"   4. Run tests: pytest {test_file}")
    print("\n📚 Documentation:")
    print(f"   • Domain README: {readme_file}")
    print(f"   • Plugin guide: docs/PLUGIN_DEVELOPMENT_GUIDE.md")
    print("\n🎯 Happy coding with BlackMamba!")
    
    return True


def list_domains(base_path: Optional[Path] = None):
    """List all available domains"""
    if base_path is None:
        base_path = Path.cwd()
    
    domains_dir = base_path / "blackmamba" / "domains"
    
    if not domains_dir.exists():
        print("❌ No domains directory found.")
        return
    
    print("📦 Available Domains:\n")
    
    domain_files = sorted(domains_dir.glob("*.py"))
    domain_files = [f for f in domain_files if f.name != "__init__.py"]
    
    if not domain_files:
        print("   No domains found.")
        return
    
    for domain_file in domain_files:
        domain_name = domain_file.stem
        print(f"   • {domain_name}")
        
        # Try to read first line of docstring
        try:
            with open(domain_file, 'r') as f:
                lines = f.readlines()
                for line in lines[1:10]:  # Check first few lines
                    if line.strip() and not line.strip().startswith('"""'):
                        if '"""' in line:
                            desc = line.split('"""')[1].strip()
                            if desc:
                                print(f"     {desc}")
                        break
        except:
            pass
    
    print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="BlackMamba CLI - Cognitive Domain Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new domain
  blackmamba new logistics "Handles supply chain optimization"
  
  # List all domains
  blackmamba list
  
  # Create a domain in a specific project
  blackmamba new medical_diagnosis "Medical equipment diagnostics" --path /path/to/project
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # New domain command
    new_parser = subparsers.add_parser("new", help="Create a new cognitive domain")
    new_parser.add_argument("name", help="Domain name (e.g., 'logistics', 'medical_diagnosis')")
    new_parser.add_argument(
        "description",
        nargs="?",
        default="Custom cognitive domain",
        help="Brief description of the domain"
    )
    new_parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Base path for the project (default: current directory)"
    )
    
    # List domains command
    list_parser = subparsers.add_parser("list", help="List all available domains")
    list_parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Base path for the project (default: current directory)"
    )
    
    args = parser.parse_args()
    
    if args.command == "new":
        success = create_domain(args.name, args.description, args.path)
        sys.exit(0 if success else 1)
    
    elif args.command == "list":
        list_domains(args.path)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
