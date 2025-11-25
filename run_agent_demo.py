#!/usr/bin/env python3
"""
Demo script for MediAI Multi-Agent System

This script demonstrates the agent-based architecture:
1. Generate sample data
2. Ingest data using DataIngestionAgent
3. Run transformations using DataTransformationAgent
4. Validate quality using DataQualityAgent
"""

import sys
import logging
from pathlib import Path

# Setup Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/agent_demo.log')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run agent demo."""
    print("\n" + "=" * 80)
    print("MediAI Multi-Agent System - Demo")
    print("=" * 80)
    print("\nThis demo will:")
    print("  1. Check if sample data exists")
    print("  2. Ingest sample data into PostgreSQL using agents")
    print("  3. Show agent execution results")
    print("\n" + "=" * 80)

    # Initialize orchestrator
    logger.info("Initializing orchestrator...")
    orchestrator = WorkflowOrchestrator()

    # Step 1: Check sample data
    print("\n[Step 1] Checking sample data...")
    data_dir = Path('data/sample')

    if not data_dir.exists():
        print(f"\n❌ Sample data not found at: {data_dir}")
        print("\n📝 Please run first:")
        print("   python scripts/generate_sample_data.py")
        sys.exit(1)

    files = list(data_dir.glob('*.csv'))
    print(f"✓ Found {len(files)} CSV files:")
    for f in files:
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"  - {f.name} ({size_mb:.1f} MB)")

    # Step 2: Run ingestion workflow
    print("\n[Step 2] Running data ingestion workflow...")
    print("This will:")
    print("  - Use DataIngestionAgent to load data")
    print("  - Use DataQualityAgent to validate data")
    print("\nStarting ingestion...\n")

    result = orchestrator.ingest_sample_data()

    # Step 3: Show results
    print("\n[Step 3] Execution Results")
    print("=" * 80)

    if result['status'] == 'success':
        print("✓ Status: SUCCESS")
        print(f"✓ Tables ingested: {result.get('tables_ingested', 0)}")

        print("\nDetails:")
        for table_name, table_result in result.get('results', {}).items():
            print(f"\n{table_name}:")
            if 'results' in table_result and 'ingestion' in table_result['results']:
                ing_result = table_result['results']['ingestion']
                if 'output' in ing_result:
                    output = ing_result['output']
                    print(f"  - Rows ingested: {output.get('rows_ingested', 0)}")
                    print(f"  - Success rate: {output.get('success_rate', 0):.1%}")

    else:
        print(f"✗ Status: FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

    # Step 4: Next steps
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("\n1. Check data in database:")
    print("   docker-compose exec postgres psql -U postgres -d mimic_iv")
    print("   SELECT COUNT(*) FROM raw.patients;")
    print("\n2. Run dbt transformations:")
    print("   python agents/orchestrator.py transform")
    print("\n3. Run quality checks:")
    print("   python agents/orchestrator.py quality --target-table raw.patients")
    print("\n4. Start API and UI:")
    print("   docker-compose up -d api streamlit")
    print("   Open http://localhost:8501")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
