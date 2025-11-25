#!/usr/bin/env python3
"""
Deployment Readiness Check for MediAI Multi-Agent System

This script validates that the multi-agent system is properly configured
and ready for local deployment.
"""

import sys
import os
from pathlib import Path
import importlib.util


def print_header(title):
    """Print section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def check_mark(status):
    """Return check mark or X."""
    return "✓" if status else "✗"


def check_file_exists(filepath):
    """Check if file exists."""
    return Path(filepath).exists()


def check_directory_structure():
    """Check if all required directories and files exist."""
    print_header("1. Directory Structure")

    required_files = {
        'agents/core/base_agent.py': 'BaseAgent implementation',
        'agents/roles/data_engineer.py': 'Data engineering agents',
        'agents/crews/data_pipeline_crew.py': 'DataPipelineCrew',
        'agents/tools/database_tool.py': 'DatabaseTool',
        'agents/tools/file_tool.py': 'FileTool',
        'agents/orchestrator.py': 'WorkflowOrchestrator',
        'agents/requirements.txt': 'Agent dependencies',
        'run_agent_demo.py': 'Demo script',
        'AGENT_DEPLOYMENT_GUIDE.md': 'Deployment guide',
        'AGENT_IMPLEMENTATION_SUMMARY.md': 'Implementation summary',
    }

    all_exist = True
    for filepath, description in required_files.items():
        exists = check_file_exists(filepath)
        all_exist = all_exist and exists
        status = check_mark(exists)
        print(f"{status} {filepath:45s} - {description}")

    return all_exist


def check_sample_data():
    """Check if sample data exists."""
    print_header("2. Sample Data")

    data_dir = Path('data/sample')
    required_files = ['patients.csv', 'icustays.csv', 'chartevents.csv']

    if not data_dir.exists():
        print("✗ Sample data directory not found")
        print("\n  Run: python scripts/generate_sample_data.py")
        return False

    all_exist = True
    for filename in required_files:
        filepath = data_dir / filename
        exists = filepath.exists()
        all_exist = all_exist and exists

        status = check_mark(exists)
        if exists:
            size_mb = filepath.stat().st_size / 1024 / 1024
            print(f"{status} {filename:20s} - {size_mb:6.2f} MB")
        else:
            print(f"{status} {filename:20s} - MISSING")

    return all_exist


def check_python_imports():
    """Check if agent modules can be imported."""
    print_header("3. Python Imports")

    modules_to_check = [
        ('agents.core.base_agent', 'BaseAgent'),
        ('agents.roles.data_engineer', 'DataIngestionAgent'),
        ('agents.crews.data_pipeline_crew', 'DataPipelineCrew'),
        ('agents.orchestrator', 'WorkflowOrchestrator'),
        ('agents.tools.database_tool', 'DatabaseTool'),
        ('agents.tools.file_tool', 'FileTool'),
    ]

    all_imported = True
    for module_name, class_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            getattr(module, class_name)
            print(f"✓ {module_name:40s} - {class_name}")
        except Exception as e:
            print(f"✗ {module_name:40s} - ERROR: {e}")
            all_imported = False

    return all_imported


def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("4. Python Dependencies")

    required_packages = [
        'pandas',
        'psycopg2',
        'sqlalchemy',
        'tqdm',
        'dotenv',
    ]

    all_installed = True
    for package_name in required_packages:
        # Handle special cases
        if package_name == 'psycopg2':
            spec = importlib.util.find_spec('psycopg2')
        elif package_name == 'dotenv':
            spec = importlib.util.find_spec('dotenv')
        else:
            spec = importlib.util.find_spec(package_name)

        installed = spec is not None
        all_installed = all_installed and installed

        status = check_mark(installed)
        print(f"{status} {package_name:20s}")

    return all_installed


def check_configuration():
    """Check if configuration files exist."""
    print_header("5. Configuration Files")

    config_files = {
        '.env': 'Environment variables',
        'docker-compose.yml': 'Docker services',
        'Makefile': 'Build commands',
    }

    all_exist = True
    for filepath, description in config_files.items():
        exists = check_file_exists(filepath)
        all_exist = all_exist and exists
        status = check_mark(exists)
        print(f"{status} {filepath:25s} - {description}")

    return all_exist


def check_makefile_commands():
    """Check if Makefile has agent commands."""
    print_header("6. Makefile Agent Commands")

    if not check_file_exists('Makefile'):
        print("✗ Makefile not found")
        return False

    with open('Makefile', 'r') as f:
        makefile_content = f.read()

    required_commands = [
        'agents-demo',
        'agents-ingest',
        'agents-transform',
        'agents-quality-check',
        'demo',
    ]

    all_exist = True
    for command in required_commands:
        exists = f"{command}:" in makefile_content
        all_exist = all_exist and exists
        status = check_mark(exists)
        print(f"{status} make {command}")

    return all_exist


def main():
    """Run all checks."""
    print("\n" + "=" * 80)
    print("  MediAI Multi-Agent System - Deployment Readiness Check")
    print("=" * 80)

    checks = [
        ("Directory Structure", check_directory_structure),
        ("Sample Data", check_sample_data),
        ("Python Imports", check_python_imports),
        ("Python Dependencies", check_dependencies),
        ("Configuration Files", check_configuration),
        ("Makefile Commands", check_makefile_commands),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            results[name] = False

    # Summary
    print_header("Summary")

    all_passed = all(results.values())
    for name, passed in results.items():
        status = check_mark(passed)
        print(f"{status} {name}")

    print("\n" + "=" * 80)
    if all_passed:
        print("✓ READY FOR DEPLOYMENT")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Run agent demo:")
        print("     python run_agent_demo.py")
        print("\n  2. Or use Makefile:")
        print("     make demo")
        print("\n  3. Check documentation:")
        print("     - AGENT_DEPLOYMENT_GUIDE.md")
        print("     - AGENT_IMPLEMENTATION_SUMMARY.md")
        return 0
    else:
        print("✗ NOT READY - Please fix the issues above")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
